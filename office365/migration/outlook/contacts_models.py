"""Contact records — the sidecar an export writes and the payload an import posts.

A contact is the simplest thing this product moves and the least forgiving about
identity: Exchange keeps no ``internetMessageId`` and no ``iCalUid``, so nothing the
source knows survives a create. What is left to recognise a re-run's own work by is
the display name plus the primary address (:func:`contact_dedup_key`), and what is
left to verify an import by is a digest of the fields it promised to restore
(:func:`contact_digest`).

Three Exchange behaviours are measured, not assumed, and each one shapes the code:

* **All the fields this module records are selectable in one ``$select``** — 31
  properties in a single read, so an export of N contacts is N content reads plus
  the folder walk.
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
from typing import Any, Dict, List, Optional, Tuple

from office365.runtime.converters.scalars import iso_or_none

#: Graph contact properties an export reads. Probed: every one of them answers in a
#: single ``$select``, and every one of them survives a create → read round trip.
CONTACT_COLUMNS = [
    "id",
    "displayName",
    "givenName",
    "surname",
    "middleName",
    "initials",
    "nickName",
    "title",
    "fileAs",
    "generation",
    "companyName",
    "department",
    "jobTitle",
    "profession",
    "manager",
    "assistantName",
    "officeLocation",
    "businessHomePage",
    "birthday",
    "personalNotes",
    "spouseName",
    "children",
    "imAddresses",
    "businessPhones",
    "homePhones",
    "mobilePhone",
    "emailAddresses",
    "categories",
    "businessAddress",
    "homeAddress",
    "otherAddress",
]

#: The five components of a Graph ``physicalAddress``, in the order they render in
#: a vCard ``ADR`` line (``pobox;extended;street;locality;region;code;country`` has
#: two empty leading components, so the mapping is explicit rather than positional).
_ADDRESS_PARTS = ("street", "city", "state", "postal_code", "country_or_region")

#: Graph spells a physical address in camelCase; the sidecar keeps snake_case like
#: every other key, so the mapping is one table both directions read.
_ADDRESS_KEYS = {
    "street": "street",
    "city": "city",
    "state": "state",
    "postal_code": "postalCode",
    "country_or_region": "countryOrRegion",
}

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
    stem = "_".join(part for part in (mail_slug(contact.get_property("displayName")), digest) if part)
    name = f"{stem or digest}.vcf"
    return f"{folder_path}/{name}" if folder_path else name


def contact_envelope(
    contact,
    folder_path: str,
    extra_properties: list[str] | None = None,
    display_path: str | None = None,
) -> dict[str, Any]:
    """The sidecar record for a contact: everything an import replays.

    All values are JSON-safe *by construction* — nested typed values go through
    ``to_json()`` and nothing is rescued by ``json.dumps(..., default=str)``, which
    is what would otherwise write a ``PhysicalAddress(city=…)`` repr that no import
    could read back.
    """
    envelope: dict[str, Any] = {
        "graph_id": contact_key(contact),
        "folder_path": folder_path,
        "folder_display_path": display_path or folder_path,
        "display_name": contact.get_property("displayName"),
        "given_name": contact.get_property("givenName"),
        "surname": contact.get_property("surname"),
        "middle_name": contact.get_property("middleName"),
        "initials": contact.get_property("initials"),
        "nick_name": contact.get_property("nickName"),
        "title": contact.get_property("title"),
        "file_as": contact.get_property("fileAs"),
        "generation": contact.get_property("generation"),
        "company_name": contact.get_property("companyName"),
        "department": contact.get_property("department"),
        "job_title": contact.get_property("jobTitle"),
        "profession": contact.get_property("profession"),
        "manager": contact.get_property("manager"),
        "assistant_name": contact.get_property("assistantName"),
        "office_location": contact.get_property("officeLocation"),
        "business_home_page": contact.get_property("businessHomePage"),
        "birthday": iso_or_none(contact.get_property("birthday")),
        "personal_notes": contact.get_property("personalNotes"),
        "spouse_name": contact.get_property("spouseName"),
        "children": [str(value) for value in (contact.get_property("children") or [])],
        "im_addresses": [str(value) for value in (contact.get_property("imAddresses") or [])],
        "business_phones": [str(value) for value in (contact.get_property("businessPhones") or [])],
        "home_phones": [str(value) for value in (contact.get_property("homePhones") or [])],
        "mobile_phone": contact.get_property("mobilePhone"),
        "email_addresses": [
            {"name": _as_dict(item).get("name"), "address": _as_dict(item).get("address")}
            for item in (contact.get_property("emailAddresses") or [])
        ],
        "categories": [str(value) for value in (contact.get_property("categories") or [])],
        "created": iso_or_none(contact.get_property("createdDateTime")),
        "modified": iso_or_none(contact.get_property("lastModifiedDateTime")),
        "vcf_path": contact_dest_path(contact, folder_path),
    }
    for side in ("business_address", "home_address", "other_address"):
        envelope[side] = _address(contact.get_property(_camel(side)))
    for name in extra_properties or []:
        envelope[name] = contact.get_property(name)
    return envelope


def contact_vcard(envelope: dict[str, Any]) -> bytes:
    """The contact as a vCard 3.0 document.

    A courtesy for other clients — the sidecar is what an import replays — but it is
    the portable artefact of an export, and because this module renders the bytes
    itself an export *can* be verified by them (unlike a mail import, where Exchange
    re-serialises everything it accepts).
    """
    name = [
        envelope.get("surname") or "",
        envelope.get("given_name") or "",
        envelope.get("middle_name") or "",
        envelope.get("title") or "",
        envelope.get("generation") or "",
    ]
    lines = [
        "BEGIN:VCARD",
        "VERSION:3.0",
        "N:" + ";".join(_vcard_escape(part) for part in name),
        "FN:" + _vcard_escape(envelope.get("display_name") or ""),
        "UID:" + _vcard_escape(envelope.get("graph_id") or ""),
    ]
    _add(lines, "NICKNAME", envelope.get("nick_name"))
    _add(lines, "TITLE", envelope.get("job_title"))
    _add(lines, "ROLE", envelope.get("profession"))
    if envelope.get("company_name") or envelope.get("department"):
        org = [envelope.get("company_name") or "", envelope.get("department") or ""]
        lines.append("ORG:" + ";".join(_vcard_escape(part) for part in org))
    _add(lines, "X-MS-OFFICE-LOCATION", envelope.get("office_location"))
    for number in envelope.get("business_phones") or []:
        lines.append(f"TEL;TYPE=WORK,VOICE:{_vcard_escape(number)}")
    for number in envelope.get("home_phones") or []:
        lines.append(f"TEL;TYPE=HOME,VOICE:{_vcard_escape(number)}")
    if envelope.get("mobile_phone"):
        lines.append(f"TEL;TYPE=CELL:{_vcard_escape(envelope['mobile_phone'])}")
    for email in envelope.get("email_addresses") or []:
        if email.get("address"):
            lines.append(f"EMAIL;TYPE=INTERNET:{_vcard_escape(email['address'])}")
    for im_address in envelope.get("im_addresses") or []:
        lines.append(f"X-MS-IMADDRESS:{_vcard_escape(im_address)}")
    for side, kind in (("business_address", "WORK"), ("home_address", "HOME"), ("other_address", "OTHER")):
        address = envelope.get(side) or {}
        if any(address.get(part) for part in _ADDRESS_PARTS):
            adr = [
                "",
                "",
                address.get("street") or "",
                address.get("city") or "",
                address.get("state") or "",
                address.get("postal_code") or "",
                address.get("country_or_region") or "",
            ]
            lines.append(f"ADR;TYPE={kind}:" + ";".join(_vcard_escape(part) for part in adr))
    birthday = _date_only(envelope.get("birthday"))
    if birthday:
        lines.append("BDAY:" + birthday)
    if envelope.get("personal_notes"):
        lines.append("NOTE:" + _vcard_escape(envelope["personal_notes"]))
    if envelope.get("categories"):
        categories = ",".join(_vcard_escape(name) for name in envelope["categories"])
        lines.append("CATEGORIES:" + categories)
    _add(lines, "URL", envelope.get("business_home_page"))
    stamp = _vcard_stamp(envelope.get("modified"))
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
        str(envelope.get("display_name") or "").strip().lower(),
        first[0][0] if first else "",
    )


def contact_create_payload(
    envelope: dict[str, Any],
    options: ContactImportOptions | None = None,
) -> dict[str, Any]:
    """The Graph ``POST /contacts`` body for a sidecar record.

    Returns Graph's own spelling so the target can post it verbatim, and omits what
    Exchange assigns itself (``id``, ``createdDateTime``, ``lastModifiedDateTime``,
    ``changeKey``, ``parentFolderId``). A contact has no ``transactionId``, so
    concurrency is handled by the target's own dedupe index rather than by the
    service.
    """
    options = options or ContactImportOptions()
    display_name = str(envelope.get("display_name") or "").strip()
    if not display_name:
        raise ValueError("the sidecar record has no display name: Exchange rejects a contact without one")
    payload: dict[str, Any] = {"displayName": display_name}
    for name, key in (
        ("givenName", "given_name"),
        ("surname", "surname"),
        ("middleName", "middle_name"),
        ("initials", "initials"),
        ("nickName", "nick_name"),
        ("title", "title"),
        ("fileAs", "file_as"),
        ("generation", "generation"),
        ("companyName", "company_name"),
        ("department", "department"),
        ("jobTitle", "job_title"),
        ("profession", "profession"),
        ("manager", "manager"),
        ("assistantName", "assistant_name"),
        ("officeLocation", "office_location"),
        ("businessHomePage", "business_home_page"),
        ("personalNotes", "personal_notes"),
        ("spouseName", "spouse_name"),
        ("mobilePhone", "mobile_phone"),
    ):
        value = envelope.get(key)
        if value:
            payload[name] = value
    for name, key in (
        ("businessPhones", "business_phones"),
        ("homePhones", "home_phones"),
        ("imAddresses", "im_addresses"),
        ("children", "children"),
    ):
        values = [str(value) for value in envelope.get(key) or [] if value]
        if values:
            payload[name] = values
    emails = [{"address": address, "name": name or address} for address, name in _email_addresses(envelope)]
    if emails:
        payload["emailAddresses"] = emails
    # ``birthday`` is a DateTimeOffset; the sidecar's ISO string is one (measured:
    # Exchange rewrites the time of day to 11:59 local and keeps the date).
    if envelope.get("birthday"):
        payload["birthday"] = envelope["birthday"]
    for side in ("business_address", "home_address", "other_address"):
        address = {_ADDRESS_KEYS[part]: value for part, value in (envelope.get(side) or {}).items() if value}
        if address:
            payload[_camel(side)] = address
    if options.restore_categories:
        categories = [str(name) for name in envelope.get("categories") or [] if name]
        # Measured: Exchange rejects the whole contact (``ErrorPropertyUpdate``,
        # "Property update did not succeed.") when one category carries a comma — the
        # vCard separates categories with it. Refuse with the offending name instead
        # of failing opaquely, and let the runner count this item as an error.
        bad = [name for name in categories if "," in name]
        if bad:
            raise ValueError(f"a contact category cannot contain a comma: {bad[0]!r}")
        if categories:
            payload["categories"] = categories
    return payload


def contact_digest(envelope: dict[str, Any], options: ContactImportOptions | None = None) -> str:
    """A digest of the fields an import restores, for verifying that it did.

    Not the ``.vcf`` bytes: the other side of an import is Exchange, which assigns the
    identifiers and reformats a birthday's time of day, so the comparable artefact is
    the *contact*. Three normalisations are measured rather than defensive: a
    birthday compares by date (Exchange stores 11:59 whatever is sent), an email
    compares as ``(address, name or address)`` (an address-only entry reads back
    named after itself), and the address components compare as strings, empty for
    absent.
    """
    options = options or ContactImportOptions()
    canonical: Dict[str, Any] = {
        "display_name": _text(envelope.get("display_name")),
        "names": [
            _text(envelope.get(name))
            for name in ("given_name", "surname", "middle_name", "initials", "nick_name", "title", "generation")
        ],
        "file_as": _text(envelope.get("file_as")),
        "org": [
            _text(envelope.get(name))
            for name in ("company_name", "department", "job_title", "profession", "manager", "assistant_name")
        ],
        "office_location": _text(envelope.get("office_location")),
        "home_page": _text(envelope.get("business_home_page")),
        "phones": [
            [_text(number) for number in envelope.get("business_phones") or []],
            [_text(number) for number in envelope.get("home_phones") or []],
            _text(envelope.get("mobile_phone")),
        ],
        "emails": _email_addresses(envelope),
        "im_addresses": sorted(_text(value) for value in envelope.get("im_addresses") or []),
        "children": sorted(_text(value) for value in envelope.get("children") or []),
        "spouse": _text(envelope.get("spouse_name")),
        "notes": _text(envelope.get("personal_notes")),
        "birthday": _date_only(envelope.get("birthday")),
        "addresses": [
            [_text((envelope.get(side) or {}).get(part)) for part in _ADDRESS_PARTS]
            for side in ("business_address", "home_address", "other_address")
        ],
    }
    if options.restore_categories:
        canonical["categories"] = sorted(_text(name) for name in envelope.get("categories") or [])
    serialized = json.dumps(canonical, sort_keys=True)
    return hashlib.md5(serialized.encode("utf-8")).hexdigest()


def _email_addresses(envelope: dict[str, Any]) -> List[Tuple[str, str]]:
    """``[(address, name or address)]``, lower-cased and sorted.

    Exchange fills in a missing ``name`` from the address (measured), so a digest
    that compared the raw pair would report every imported contact as a mismatch.
    """
    pairs: List[Tuple[str, str]] = []
    for entry in envelope.get("email_addresses") or []:
        address = str(_as_dict(entry).get("address") or "").strip().lower()
        if not address:
            continue
        name = str(_as_dict(entry).get("name") or "").strip() or address
        pairs.append((address, name))
    return sorted(pairs)


def _address(value: Any) -> Dict[str, Optional[str]]:
    """A Graph ``physicalAddress`` as a plain dict of its five parts."""
    source = _as_dict(value)
    return {part: source.get(_ADDRESS_KEYS[part]) or None for part in _ADDRESS_PARTS}


def _as_dict(value: Any) -> Dict[str, Any]:
    """A Graph nested value as a plain dict.

    A fetched contact hands back *typed* ``ClientValue`` objects (``homeAddress`` is
    a ``PhysicalAddress``, each email an ``EmailAddress``), so the raw bag is only
    reachable through ``to_json()`` — ``get_property`` returns the wrapper.
    """
    if value is None:
        return {}
    if isinstance(value, dict):
        return value
    to_json = getattr(value, "to_json", None)
    if callable(to_json):
        payload = to_json()
        if isinstance(payload, dict):
            return payload
    properties = getattr(value, "properties", None)
    return properties if isinstance(properties, dict) else {}


def _camel(name: str) -> str:
    """``business_address`` → ``businessAddress`` (the Graph spelling)."""
    head, *tail = name.split("_")
    return head + "".join(part.title() for part in tail)


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
