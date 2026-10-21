"""Contact records — one contact's sidecar, and the artefacts a migration builds from it.

The sidecar *is* the contact as Graph spells it: ``Contact.to_json()`` already answers
every column the export selected, with the typed values flattened by the library's own
serialiser. This module therefore owns no field list. It owns three things:

* **provenance** — the folder the contact came from and the ``.vcf`` beside it, which
  a model cannot know;
* **the two normalisations Exchange forces on a round trip** (a birthday compares by
  date, an address-only email reads back named after itself);
* **the artefacts** — a POST body, a digest, a vCard.

A record is built *from* a model (``ContactRecord.of(contact, folder)``) but never holds
one: the payload is the contract, so a record can be re-read from disk with no client,
no context and no entity — which is what lets an import verify a sidecar against a
contact the service returned, on two machines, with the same code.

Three Exchange behaviours are measured, not assumed:

* **The whole contact is selectable in one ``$select``** — every column the model
  declares, so an export of N contacts is N content reads plus the folder walk.
* **A birthday is normalised to a fixed time of day.** ``1953-05-01T00:00:00Z`` and
  ``1953-05-01T11:59:00+00:00`` are both stored as, and read back as,
  ``1953-05-01 11:59:00+00:00`` — so the digest compares the *date*, and a replay
  may send back either form.
* **An ``emailAddresses`` entry sent without a ``name`` comes back with ``name`` set
  to the address**, so the digest compares ``name or address`` rather than failing
  every round trip on that fill-in.

A contact's **photo** is a sub-resource, and neither end is cheap: the ``contact``
entity does not expose a ``hasPhoto`` column on this endpoint (measured — it is not
in a full read), so finding out costs one ``GET /photo`` that 404s
(``ErrorItemNotFound``) per contact without one. Photos are therefore out of scope
and reported as such in the fidelity matrix, rather than probed for one request per
contact in a run that may have thousands.
"""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Mapping, Tuple

from office365.outlook.contacts.contact import Contact

#: Graph contact properties an export reads: every column the model declares. Derived
#: rather than listed, for the reason the calendar projection is: a hand-kept list drifts
#: from the getters that consume it, and a ``$select`` that omits a column is
#: indistinguishable from a contact that has no value for it.
CONTACT_COLUMNS = Contact.select_all()

#: What Exchange assigns to a contact, so an import must not replay it.
_SERVER_ASSIGNED = frozenset(
    {"id", "changeKey", "parentFolderId", "primaryEmailAddress", "createdDateTime", "lastModifiedDateTime"}
)
#: The sidecar's remaining vocabulary needs no list of its own: a field is a contact field
#: if the model declares it, which is why this is the projection minus that set — a column
#: the model gains is exported, replayed and verified without a function here changing, and
#: the export's own bookkeeping is excluded for the same reason: not being declared.
_RESTORED = frozenset(CONTACT_COLUMNS) - _SERVER_ASSIGNED

#: The keys this module adds to the model's payload — the only vocabulary it owns.
_FOLDER_KEY = "folder_path"
_DISPLAY_KEY = "folder_display_path"
_VCF_KEY = "vcf_path"
_PROVENANCE = (_FOLDER_KEY, _DISPLAY_KEY, _VCF_KEY)
assert not set(_PROVENANCE) & frozenset(CONTACT_COLUMNS), "a provenance key collides with a declared column"

#: The five components of a Graph ``physicalAddress`` in the order a vCard ``ADR`` line
#: renders them — ``pobox;extended;street;locality;region;code;country`` has two empty
#: leading components, so the order is stated rather than taken from the dict.
_ADR_PARTS = ("street", "city", "state", "postalCode", "countryOrRegion")
_ADDRESS_KEYS = ("businessAddress", "homeAddress", "otherAddress")


def _as_is(value: Any) -> Any:
    """A column with no declared rule compares as it stands."""
    return value


def _by_date(value: Any) -> str:
    """The ``YYYY-MM-DD`` a birthday falls on, whatever time of day is attached.

    Exchange normalises a birthday to 11:59 in the mailbox's zone and reads it back
    that way (measured — both ``T00:00:00Z`` and ``T11:59:00+00:00`` come back as
    ``… 11:59:00+00:00``), so comparing the instant would fail every round trip over
    a time of day the user never set.
    """
    if isinstance(value, datetime):
        return str(value)[:10]
    match = re.match(r"^(\d{4})-(\d{2})-(\d{2})", str(value or "").strip())
    return "-".join(match.groups()) if match else str(value or "").strip()


def _unordered(value: Any) -> List[str]:
    """A label a service keeps unordered compares as a set."""
    return sorted(str(item).strip() for item in value or [])


def _email_pairs(value: Any) -> List[Tuple[str, str]]:
    """An address book entry compares as ``(address, name or address)``.

    Exchange fills a missing ``name`` in from the address (measured), so comparing the
    raw pair would report every imported contact as a mismatch.
    """
    pairs = []
    for entry in value or []:
        address = str((entry or {}).get("address") or "").strip().lower()
        if address:
            pairs.append((address, str(entry.get("name") or "").strip() or address))
    return sorted(pairs)


def _address(value: Any) -> Dict[str, str]:
    """A partial address is the whole answer, so the parts it omits are not a difference."""
    return {part: text for part, text in (value or {}).items() if text}


#: How two values of a column are equivalent, by attribute name. A column not named here
#: compares as it stands. The wire spellings are resolved from the model's own getters,
#: so this table cannot drift from the declarations that fill the payload.
_RULES = (
    ("birthday", _by_date),
    ("categories", _unordered),
    ("children", _unordered),
    ("im_addresses", _unordered),
    ("email_addresses", _email_pairs),
    ("business_address", _address),
    ("home_address", _address),
    ("other_address", _address),
)
assert all(hasattr(Contact, attr) for attr, _ in _RULES), "a rule names an attribute the model does not declare"
_COMPARE: Dict[str, Any] = {Contact.wire_name(attr): rule for attr, rule in _RULES}

#: RFC 6350 §3.1 caps a content line at 75 octets; a continuation starts with a space.
_MAX_LINE_OCTETS = 75

#: Digits in a vCard ``REV`` stamp: ``YYYYMMDD`` + ``HHMMSS``.
_REV_DIGITS = 14

_VCARD_ESCAPED = re.compile(r"([\\;,])")
_NEWLINES = re.compile(r"\r?\n")


@dataclass
class ContactExportOptions:
    """What a contact export includes."""

    #: Name of the top folder in the export tree (``None`` uses the contact folder's
    #: own display name, slugified). Set it to keep a stable root across renames.
    root_name: str | None = None
    #: Walk the folder's child folders too. On by default: contact folders nest, and
    #: an export that silently dropped ``Vendors`` under ``Work`` would be a loss the
    #: fidelity matrix does not declare.
    include_subfolders: bool = True
    #: Extra Graph contact properties to record in the sidecar (camelCase names).
    extra_properties: list[str] = field(default_factory=list)


@dataclass
class ContactImportOptions:
    """What an import of an exported contact tree restores.

    Pass the *same* options object to both adapters of an import job: the source
    computes the content digest of what the target promises to restore, so the two
    sides have to agree on the fields to be comparable (see :meth:`ContactRecord.digest`).
    """

    #: Re-apply the category labels.
    restore_categories: bool = True


class ContactRecord:
    """One contact as the export records it: Graph's payload plus where it came from.

    ``payload`` is the sidecar contract — the model's ``to_json()`` output, so a column
    the model gains is exported, replayed and verified with nothing here edited. Build
    one from a loaded contact with :meth:`of`, or from a sidecar on disk with
    :meth:`from_json`; either way the record needs no client and no context.
    """

    __slots__ = ("_json",)

    def __init__(self, payload: Mapping[str, Any], folder_path: str = "", display_path: str | None = None) -> None:
        self._json: Dict[str, Any] = dict(payload, **{_FOLDER_KEY: folder_path})
        self._json[_DISPLAY_KEY] = display_path or folder_path
        self._json.setdefault(_VCF_KEY, self.dest_path)

    @classmethod
    def of(
        cls,
        contact: Contact,
        folder_path: str = "",
        extra_properties: List[str] | None = None,
        display_path: str | None = None,
    ) -> ContactRecord:
        """The record for a contact read from the service: its payload, plus provenance.

        Nothing is copied field by field, so a column the model gains is exported and
        replayed without this method changing. All values are JSON-safe *by construction*
        — they came from a JSON response and went through ``to_json()`` — and none is
        rescued by ``json.dumps(..., default=str)``, which is what would otherwise write a
        ``PhysicalAddress(city=…)`` repr.
        """
        payload = dict(contact.to_json())
        for name in extra_properties or []:
            payload[name] = contact.get_property(name)
        return cls(payload, folder_path, display_path)

    @classmethod
    def from_json(cls, payload: Mapping[str, Any]) -> ContactRecord:
        """The record a sidecar file holds: read back verbatim, no entity involved."""
        return cls(payload, str(payload.get(_FOLDER_KEY) or ""), payload.get(_DISPLAY_KEY))

    def to_json(self) -> Dict[str, Any]:
        """The sidecar as it is written to disk."""
        return dict(self._json)

    @property
    def folder_path(self) -> str:
        return str(self._json.get(_FOLDER_KEY) or "")

    @property
    def id(self) -> str:
        """The Graph id this record is keyed by — the only identity a contact has.

        Nothing else the source knows survives the create: Exchange assigns no
        ``internetMessageId``/``iCalUid`` equivalent, and the id is stable for the
        contact's life in its folder, so a re-run finds the record it wrote.
        """
        return str(self._json.get("id") or "")

    @property
    def dest_path(self) -> str:
        """``<folder>/<name slug>_<id digest>.vcf``: deterministic, so a re-run finds it.

        The name is the display name rather than a date: a contact has no meaningful
        instant to sort by (the created stamp is Exchange's), and a human browsing the
        tree expects to find people by name.
        """
        from office365.migration.outlook.models import mail_slug  # local: avoid a cycle at import time

        digest = hashlib.sha1(self.id.encode("utf-8")).hexdigest()[:8]
        stem = "_".join(part for part in (mail_slug(self._json.get("displayName")), digest) if part)
        name = f"{stem or digest}.vcf"
        return f"{self.folder_path}/{name}" if self.folder_path else name

    @property
    def dedup_key(self) -> Tuple[str, str]:
        """Display name and first address: what a target recognises a re-run's work by.

        Matching on the name alone would merge two different people who happen to share
        one, and nothing else survives the create.
        """
        pairs = self.email_pairs
        return (str(self._json.get("displayName") or "").strip().lower(), pairs[0][0] if pairs else "")

    @property
    def email_pairs(self) -> List[Tuple[str, str]]:
        """``[(address, name or address)]``, lower-cased and sorted.

        Exchange fills in a missing ``name`` from the address (measured), so comparing
        the raw pair would report every imported contact as a mismatch.
        """
        return _email_pairs(self._json.get("emailAddresses"))

    def restored(self) -> Dict[str, Any]:
        """The fields an import replays: the model's payload minus what Exchange assigns."""
        return {key: value for key, value in self._json.items() if key in _RESTORED}

    def payload(self, options: ContactImportOptions | None = None) -> Dict[str, Any]:
        """The Graph ``POST /contacts`` body for this record.

        A contact has no ``transactionId``, so concurrency is handled by the target's own
        dedupe index rather than by the service.
        """
        options = options or ContactImportOptions()
        body = {key: value for key, value in self.restored().items() if value}
        display_name = str(body.get("displayName") or "").strip()
        if not display_name:
            raise ValueError("the sidecar record has no display name: Exchange rejects a contact without one")
        # Mandatory, and the sidecar may hold it unstripped — set last, from the value
        # this method validated.
        body["displayName"] = display_name
        if options.restore_categories:
            # Measured: Exchange rejects the whole contact (``ErrorPropertyUpdate``,
            # "Property update did not succeed.") when one category carries a comma — the
            # vCard separates categories with it. Refuse with the offending name instead
            # of failing opaquely, and let the runner count this item as an error.
            bad = [name for name in body.get("categories") or [] if "," in str(name)]
            if bad:
                raise ValueError(f"a contact category cannot contain a comma: {bad[0]!r}")
        else:
            body.pop("categories", None)
        return body

    def digest(self, options: ContactImportOptions | None = None) -> str:
        """A digest of the fields an import restores, for verifying that it did.

        Not the ``.vcf`` bytes: the other side of an import is Exchange, which assigns the
        identifiers and reformats what it is given, so the comparable artefact is the
        *contact* — the record an import replays, which is the sidecar minus what the
        service owns.
        """
        canonical = json.dumps(self.canonical(options), sort_keys=True).encode("utf-8")
        return hashlib.md5(canonical).hexdigest()

    def canonical(self, options: ContactImportOptions | None = None) -> Dict[str, Any]:
        """The restored fields in comparable form: one rule per column, no field-by-field code.

        Only the fields the model declares take part, so a sidecar's own keys (the folder
        it came from, its ``.vcf``, a manifest's size) cannot make an export disagree with
        the import that replays it.
        """
        options = options or ContactImportOptions()
        restored = self.restored()
        if not options.restore_categories:
            restored.pop("categories", None)
        # A field the sidecar omits and a field Exchange answers empty are the same
        # statement, so empties leave the canonical form — which is what lets one digest
        # span "not recorded" and "recorded as nothing".
        restored = {key: value for key, value in restored.items() if value not in ("", [], {})}
        return {key: _COMPARE.get(key, _as_is)(value) for key, value in restored.items()}

    def vcard(self) -> bytes:
        """The contact as a vCard 3.0 document.

        A courtesy for other clients — the sidecar is what an import replays — but it is
        the portable artefact of an export, and because this module renders the bytes
        itself an export *can* be verified by them (unlike a mail import, where Exchange
        re-serialises everything it accepts).
        """
        contact = self._json
        name = [contact.get(part) for part in ("surname", "givenName", "middleName", "title", "generation")]
        lines = [
            "BEGIN:VCARD",
            "VERSION:3.0",
            "N:" + ";".join(_vcard_escape(part) for part in name),
            "FN:" + _vcard_escape(contact.get("displayName")),
            "UID:" + _vcard_escape(contact.get("id")),
        ]
        _add(lines, "NICKNAME", contact.get("nickName"))
        _add(lines, "TITLE", contact.get("jobTitle"))
        _add(lines, "ROLE", contact.get("profession"))
        if contact.get("companyName") or contact.get("department"):
            org = [contact.get("companyName"), contact.get("department")]
            lines.append("ORG:" + ";".join(_vcard_escape(part) for part in org))
        _add(lines, "X-MS-OFFICE-LOCATION", contact.get("officeLocation"))
        for number in contact.get("businessPhones") or []:
            lines.append(f"TEL;TYPE=WORK,VOICE:{_vcard_escape(number)}")
        for number in contact.get("homePhones") or []:
            lines.append(f"TEL;TYPE=HOME,VOICE:{_vcard_escape(number)}")
        if contact.get("mobilePhone"):
            lines.append(f"TEL;TYPE=CELL:{_vcard_escape(contact['mobilePhone'])}")
        for email in contact.get("emailAddresses") or []:
            if email.get("address"):
                lines.append(f"EMAIL;TYPE=INTERNET:{_vcard_escape(email['address'])}")
        for im_address in contact.get("imAddresses") or []:
            lines.append(f"X-MS-IMADDRESS:{_vcard_escape(im_address)}")
        for side, kind in zip(_ADDRESS_KEYS, ("WORK", "HOME", "OTHER")):
            address = contact.get(side) or {}
            if any(address.get(part) for part in _ADR_PARTS):
                # The two empty leading components are ``pobox`` and ``extended``, which
                # Graph does not model.
                adr = ["", ""] + [_vcard_escape(address.get(part)) for part in _ADR_PARTS]
                lines.append(f"ADR;TYPE={kind}:" + ";".join(adr))
        birthday = _by_date(contact.get("birthday"))
        if birthday:
            lines.append("BDAY:" + birthday)
        if contact.get("personalNotes"):
            lines.append("NOTE:" + _vcard_escape(contact["personalNotes"]))
        if contact.get("categories"):
            lines.append("CATEGORIES:" + ",".join(_vcard_escape(label) for label in contact["categories"]))
        _add(lines, "URL", contact.get("businessHomePage"))
        stamp = _vcard_stamp(contact.get("lastModifiedDateTime"))
        if stamp:
            lines.append("REV:" + stamp)
        lines.append("END:VCARD")
        return "".join(_vcard_fold(line) + "\r\n" for line in lines).encode("utf-8")


def _vcard_stamp(value: Any) -> str:
    """An ISO timestamp as a vCard ``REV`` value (``YYYYMMDDTHHMMSSZ``)."""
    if not value:
        return ""
    text = re.sub(r"[^0-9]", "", str(value))
    # A vCard REV is ``YYYYMMDDTHHMMSSZ``: the digits carry the instant, the zone is ours.
    stamp = text[:_REV_DIGITS]
    return stamp + "Z" if len(stamp) == _REV_DIGITS else ""


def _vcard_escape(value: Any) -> str:
    """Escape a vCard TEXT value (RFC 6350 §3.4): backslash, comma, semicolon, newline."""
    text = _VCARD_ESCAPED.sub(r"\\\1", str(value if value is not None else ""))
    return _NEWLINES.sub(r"\\n", text)


def _vcard_fold(line: str) -> str:
    """Fold a content line at 75 octets without splitting a UTF-8 sequence."""
    if len(line.encode("utf-8")) <= _MAX_LINE_OCTETS:
        return line
    chunks: List[str] = []
    current = ""
    for char in line:
        if len((current + char).encode("utf-8")) > _MAX_LINE_OCTETS:
            chunks.append(current)
            current = " " + char  # a continuation starts with a space and counts toward the octets
        else:
            current += char
    chunks.append(current)
    return "\r\n".join(chunks)


def _add(lines: List[str], name: str, value: Any) -> None:
    """Append ``NAME:value`` when the value is set."""
    if value:
        lines.append(f"{name}:{_vcard_escape(value)}")


__all__ = [
    "CONTACT_COLUMNS",
    "ContactExportOptions",
    "ContactImportOptions",
    "ContactRecord",
]
