"""Contact records — the sidecar an export writes and the payload an import posts.

A contact is the simplest thing this product moves and the least forgiving about
identity: Exchange keeps no ``internetMessageId`` and no ``iCalUid``, so nothing the
source knows survives a create. What is left to recognise a re-run's own work by is
the display name plus the primary address (:func:`contact_dedup_key`), and what is
left to verify an import by is a digest of the fields it promised to restore
(:func:`contact_digest`).

**The sidecar is the contact as Graph spells it.** ``Contact.to_json()`` already
answers every column the export selected, with the typed values flattened by the
library's own serialiser, so an export adds only what a model cannot know — the folder
the contact came from and the ``.vcf`` beside it — and an import posts that record back
minus what Exchange assigns. Nothing here enumerates contact fields: add a column to
the model and it is exported, recorded, replayed and verified without this module
changing.

Three Exchange behaviours are measured, not assumed, and each one shapes the code:

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
from typing import Any, Dict, List, Tuple

from office365.outlook.contacts.contact import Contact

#: Graph contact properties an export reads: every column the model declares.
#: Derived rather than listed, for the reason the calendar projection is: a hand-kept
#: list drifts from the getters that consume it, and a ``$select`` that omits a column
#: is indistinguishable from a contact that has no value for it.
CONTACT_COLUMNS = Contact.select_all()

#: What Exchange assigns to a contact, so an import must not replay it. The sidecar's
#: remaining vocabulary needs no list of its own: a field is a contact field if the model
#: declares it, which is why :data:`_RESTORED` is the projection minus this set — a column
#: the model gains is exported, replayed and verified without a function here changing,
#: and the export's own bookkeeping (``folder_path``, ``vcf_path``, a manifest's
#: ``source_id``/``size_bytes``) is excluded for the same reason: not being declared.
_SERVER_ASSIGNED = frozenset(
    {"id", "changeKey", "parentFolderId", "primaryEmailAddress", "createdDateTime", "lastModifiedDateTime"}
)
_RESTORED = frozenset(CONTACT_COLUMNS) - _SERVER_ASSIGNED

#: The five components of a Graph ``physicalAddress`` in the order a vCard ``ADR`` line
#: renders them — ``pobox;extended;street;locality;region;code;country`` has two empty
#: leading components, so the order is stated rather than taken from the dict.
_ADR_PARTS = ("street", "city", "state", "postalCode", "countryOrRegion")

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
    sides have to agree on the fields to be comparable (see :func:`contact_digest`).
    """

    #: Re-apply the category labels.
    restore_categories: bool = True


def contact_key(contact) -> str:
    """The identity an export is keyed by: the Graph contact id.

    A contact has no second identity to fall back on — Exchange assigns no
    ``internetMessageId``/``iCalUid`` equivalent — and the id is stable for the
    contact's life in its folder, so a re-run finds the record it wrote.
    """
    return str(contact.id or "")


def contact_dest_path(contact, folder_path: str) -> str:
    """The export path for a contact: ``<folder>/<name slug>_<id digest>.vcf``.

    Deterministic for a given contact, so a re-run finds the file it wrote. The name
    is the display name rather than a date: a contact has no meaningful instant to
    sort by (the created stamp is Exchange's), and a human browsing the tree expects
    to find people by name.
    """
    from office365.migration.outlook.models import mail_slug  # local: avoid a cycle at import time

    digest = hashlib.sha1(contact_key(contact).encode("utf-8")).hexdigest()[:8]
    stem = "_".join(part for part in (mail_slug(contact.display_name), digest) if part)
    name = f"{stem or digest}.vcf"
    return f"{folder_path}/{name}" if folder_path else name


def contact_envelope(
    contact,
    folder_path: str,
    extra_properties: list[str] | None = None,
    display_path: str | None = None,
) -> dict[str, Any]:
    """The sidecar record for a contact: the model's own payload, plus where it came from.

    ``contact.to_json()`` is the contact as Graph spells it — every column the export
    selected, with ``PhysicalAddress``/``EmailAddress`` values already flattened by the
    runtime's serialiser — so the only keys added here are the ones a model cannot
    know: the folder the contact lives in, the ``.vcf`` beside it, and any extra column
    the export was asked to record. Nothing is copied field by field, so a column the
    model gains is exported and replayed without this function changing.

    All values are JSON-safe *by construction* — they came from a JSON response and went
    through ``to_json()`` — and none is rescued by ``json.dumps(..., default=str)``,
    which is what would otherwise write a ``PhysicalAddress(city=…)`` repr.
    """
    envelope = contact.to_json()
    envelope.update(
        folder_path=folder_path,
        folder_display_path=display_path or folder_path,
        vcf_path=contact_dest_path(contact, folder_path),
    )
    for name in extra_properties or []:
        envelope[name] = contact.get_property(name)
    return envelope


def contact_vcard(envelope: dict[str, Any]) -> bytes:
    """The contact as a vCard 3.0 document.

    A courtesy for other clients — the sidecar is what an import replays — but it is
    the portable artefact of an export, and because this module renders the bytes
    itself an export *can* be verified by them (unlike a mail import, where Exchange
    re-serialises everything it accepts).

    Reads the sidecar, so it names the fields in Graph's spelling like the rest of the
    record does — the same keys ``to_json()`` wrote and ``contact_create_payload``
    posts.
    """
    name = [
        envelope.get("surname") or "",
        envelope.get("givenName") or "",
        envelope.get("middleName") or "",
        envelope.get("title") or "",
        envelope.get("generation") or "",
    ]
    lines = [
        "BEGIN:VCARD",
        "VERSION:3.0",
        "N:" + ";".join(_vcard_escape(part) for part in name),
        "FN:" + _vcard_escape(envelope.get("displayName") or ""),
        "UID:" + _vcard_escape(envelope.get("id") or ""),
    ]
    _add(lines, "NICKNAME", envelope.get("nickName"))
    _add(lines, "TITLE", envelope.get("jobTitle"))
    _add(lines, "ROLE", envelope.get("profession"))
    if envelope.get("companyName") or envelope.get("department"):
        org = [envelope.get("companyName") or "", envelope.get("department") or ""]
        lines.append("ORG:" + ";".join(_vcard_escape(part) for part in org))
    _add(lines, "X-MS-OFFICE-LOCATION", envelope.get("officeLocation"))
    for number in envelope.get("businessPhones") or []:
        lines.append(f"TEL;TYPE=WORK,VOICE:{_vcard_escape(number)}")
    for number in envelope.get("homePhones") or []:
        lines.append(f"TEL;TYPE=HOME,VOICE:{_vcard_escape(number)}")
    if envelope.get("mobilePhone"):
        lines.append(f"TEL;TYPE=CELL:{_vcard_escape(envelope['mobilePhone'])}")
    for email in envelope.get("emailAddresses") or []:
        if email.get("address"):
            lines.append(f"EMAIL;TYPE=INTERNET:{_vcard_escape(email['address'])}")
    for im_address in envelope.get("imAddresses") or []:
        lines.append(f"X-MS-IMADDRESS:{_vcard_escape(im_address)}")
    for side, kind in (("businessAddress", "WORK"), ("homeAddress", "HOME"), ("otherAddress", "OTHER")):
        address = envelope.get(side) or {}
        if any(address.get(part) for part in _ADR_PARTS):
            # The two empty leading components are ``pobox`` and ``extended``, which
            # Graph does not model.
            adr = ["", ""] + [_vcard_escape(address.get(part) or "") for part in _ADR_PARTS]
            lines.append(f"ADR;TYPE={kind}:" + ";".join(adr))
    birthday = _date_only(envelope.get("birthday"))
    if birthday:
        lines.append("BDAY:" + birthday)
    if envelope.get("personalNotes"):
        lines.append("NOTE:" + _vcard_escape(envelope["personalNotes"]))
    if envelope.get("categories"):
        categories = ",".join(_vcard_escape(name) for name in envelope["categories"])
        lines.append("CATEGORIES:" + categories)
    _add(lines, "URL", envelope.get("businessHomePage"))
    stamp = _vcard_stamp(envelope.get("lastModifiedDateTime"))
    if stamp:
        lines.append("REV:" + stamp)
    lines.append("END:VCARD")
    return "".join(_vcard_fold(line) + "\r\n" for line in lines).encode("utf-8")


def contact_dedup_key(envelope: dict[str, Any]) -> tuple[str, str]:
    """The key a target matches an existing contact on: display name and first address.

    Nothing the source knows survives the create (Exchange assigns a fresh id and
    keeps no external identifier), so this is what is left to recognise a re-run's
    own work by. Matching on the name alone would merge two different people who
    happen to share one.
    """
    first = _email_addresses(envelope)
    return (
        str(envelope.get("displayName") or "").strip().lower(),
        first[0][0] if first else "",
    )


def contact_create_payload(
    envelope: dict[str, Any],
    options: ContactImportOptions | None = None,
) -> dict[str, Any]:
    """The Graph ``POST /contacts`` body for a sidecar record.

    The sidecar *is* a contact as Graph spells it, so the body is that record: replaying
    a contact is posting it back, restricted to the fields the model declares (minus the
    ones Exchange assigns) — so a column the model gains is posted here without being
    named, and the export's own bookkeeping is not. An address-only email entry is posted
    as it stands; Exchange names it after the address, which is the fill-in
    :func:`contact_digest` allows for.

    A contact has no ``transactionId``, so concurrency is handled by the target's own
    dedupe index rather than by the service.
    """
    options = options or ContactImportOptions()
    payload = {key: value for key, value in envelope.items() if value and key in _RESTORED}
    display_name = str(payload.get("displayName") or "").strip()
    if not display_name:
        raise ValueError("the sidecar record has no display name: Exchange rejects a contact without one")
    # Mandatory, and the sidecar may hold it unstripped — so it is set last, from the
    # value this function validated.
    payload["displayName"] = display_name
    if options.restore_categories:
        # Measured: Exchange rejects the whole contact (``ErrorPropertyUpdate``,
        # "Property update did not succeed.") when one category carries a comma — the
        # vCard separates categories with it. Refuse with the offending name instead
        # of failing opaquely, and let the runner count this item as an error.
        bad = [name for name in payload.get("categories") or [] if "," in str(name)]
        if bad:
            raise ValueError(f"a contact category cannot contain a comma: {bad[0]!r}")
    else:
        payload.pop("categories", None)
    return payload


def contact_digest(envelope: dict[str, Any], options: ContactImportOptions | None = None) -> str:
    """A digest of the fields an import restores, for verifying that it did.

    Not the ``.vcf`` bytes: the other side of an import is Exchange, which assigns the
    identifiers and reformats what it is given, so the comparable artefact is the
    *contact* — the record an import replays, which is the sidecar minus what the
    service owns. Three normalisations are measured rather than defensive: a birthday
    compares by date (Exchange stores 11:59 whatever is sent), an email compares as
    ``(address, name or address)`` (an address-only entry reads back named after
    itself), and the labels a service keeps unordered compare sorted.

    Only the fields the model declares take part, so a sidecar's own keys (the folder it
    came from, its ``.vcf``, a manifest's size) cannot make an export disagree with the
    import that replays it.
    """
    options = options or ContactImportOptions()
    restored = {key: value for key, value in envelope.items() if key in _RESTORED}
    if not options.restore_categories:
        restored.pop("categories", None)
    canonical: Dict[str, Any] = {key: _comparable(value) for key, value in restored.items()}
    canonical["birthday"] = _date_only(envelope.get("birthday"))
    canonical["emailAddresses"] = _email_addresses(envelope)
    for side in ("businessAddress", "homeAddress", "otherAddress"):
        canonical[side] = [_text((envelope.get(side) or {}).get(part)) for part in _ADR_PARTS]
    for name in ("children", "imAddresses", "categories"):
        if name in canonical:
            canonical[name] = sorted(_text(value) for value in canonical[name] or [])
    # A field the sidecar omits and a field Exchange answers empty are the same
    # statement, so empties leave the canonical form — which is what lets one digest
    # span the difference between "not recorded" and "recorded as nothing".
    canonical = {key: value for key, value in canonical.items() if value not in ("", [], {})}
    return hashlib.md5(json.dumps(canonical, sort_keys=True).encode("utf-8")).hexdigest()


def _email_addresses(envelope: dict[str, Any]) -> List[Tuple[str, str]]:
    """``[(address, name or address)]``, lower-cased and sorted.

    Exchange fills in a missing ``name`` from the address (measured), so a digest
    that compared the raw pair would report every imported contact as a mismatch.
    """
    pairs: List[Tuple[str, str]] = []
    for entry in envelope.get("emailAddresses") or []:
        address = str(entry.get("address") or "").strip().lower()
        if not address:
            continue
        name = str(entry.get("name") or "").strip() or address
        pairs.append((address, name))
    return sorted(pairs)


def _comparable(value: Any) -> Any:
    """A JSON value with the noise a service adds removed: text stripped, ``None`` as ``""``."""
    if value is None:
        return ""
    if isinstance(value, str):
        return value.strip()
    if isinstance(value, list):
        return [_comparable(item) for item in value]
    if isinstance(value, dict):
        return {key: _comparable(item) for key, item in value.items()}
    return value


def _text(value: Any) -> str:
    """A comparable string for a field that may be absent or ``None``."""
    return "" if value is None else str(value).strip()


def _date_only(value: Any) -> str:
    """The ``YYYY-MM-DD`` a birthday falls on, whatever time of day is attached.

    Exchange normalises a birthday to 11:59 in the mailbox's zone and reads it back
    that way (measured — both ``T00:00:00Z`` and ``T11:59:00+00:00`` come back as
    ``… 11:59:00+00:00``), so comparing the instant would fail every round trip over
    a time of day the user never set.
    """
    if not value:
        return ""
    if isinstance(value, datetime):
        return str(value)[:10]
    match = re.match(r"^(\d{4})-(\d{2})-(\d{2})", str(value).strip())
    return "-".join(match.groups()) if match else str(value).strip()


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
    "contact_create_payload",
    "contact_dedup_key",
    "contact_dest_path",
    "contact_digest",
    "contact_envelope",
    "contact_key",
    "contact_vcard",
]
