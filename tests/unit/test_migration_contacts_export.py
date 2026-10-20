"""Contact export: a Graph contact folder as a source, a vCard tree as the target (offline).

The transport scripts Graph the way the Exchange-backed endpoint answers: one page of
contacts for the folder, one page of child folders. The contact below is the shape a
real one comes back as — ``businessAddress`` is a typed ``PhysicalAddress``, each
``emailAddresses`` entry a typed ``EmailAddress``, and ``birthday`` a parsed datetime
carrying Exchange's fixed ``11:59`` time of day (all measured live).
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from office365.graph_client import GraphClient
from office365.migration import MigrationJob
from office365.migration.outlook import (
    MANIFEST_NAME,
    ContactExportOptions,
    ContactSource,
    VcfExportTarget,
    contact_digest,
    contact_vcard,
)
from office365.migration.outlook.contacts_models import CONTACT_COLUMNS
from office365.outlook.contacts.contact import Contact
from tests._scripted_transport import MethodRoutingTransport

_FOLDER = {"id": "f1", "displayName": "Contacts"}

_ALICE = {
    "id": "c1",
    "displayName": "Alice Example",
    "givenName": "Alice",
    "surname": "Example",
    "middleName": "B",
    "initials": "AB",
    "nickName": "Al",
    "title": "Dr.",
    "fileAs": "Example, Alice",
    "generation": "Jr.",
    "companyName": "Contoso",
    "department": "Finance",
    "jobTitle": "Controller",
    "profession": "Accountant",
    "manager": "Bob Boss",
    "assistantName": "Cara Help",
    "officeLocation": "HQ 3",
    "businessHomePage": "https://contoso.example/alice",
    "birthday": "1953-05-01T11:59:00+00:00",
    "personalNotes": "Line one\nLine two; with comma, and semicolon",
    "spouseName": "Sam Example",
    "children": ["Kim"],
    "imAddresses": ["sip:alice@contoso.com"],
    "businessPhones": ["+1 555 0100", "+1 555 0101"],
    "homePhones": ["+1 555 0199"],
    "mobilePhone": "+1 555 0150",
    "emailAddresses": [
        {"name": "Alice Example", "address": "alice@contoso.com"},
        {"name": "alice@contoso.example", "address": "alice@contoso.example"},
    ],
    "categories": ["Finance", "Board, quarterly"],
    "businessAddress": {
        "street": "1 Main St",
        "city": "Springfield",
        "state": "IL",
        "postalCode": "62701",
        "countryOrRegion": "USA",
    },
    "homeAddress": {},
    "otherAddress": {"city": "Kyiv"},
    "createdDateTime": "2020-01-02T03:04:05Z",
    "lastModifiedDateTime": "2021-02-03T04:05:06Z",
}

#: An address-only email entry: Exchange reads it back named after itself (measured),
#: which is why the digest compares ``name or address`` rather than the raw pair.
_MINIMAL = {
    "id": "c2",
    "displayName": "Bob Example",
    "givenName": "Bob",
    "surname": "Example",
    "emailAddresses": [{"name": "bob@contoso.com", "address": "bob@contoso.com"}],
    "createdDateTime": "2020-02-02T03:04:05Z",
    "lastModifiedDateTime": "2020-02-02T03:04:05Z",
}

_VENDOR = {
    "id": "c3",
    "displayName": "Vendor Ltd",
    "companyName": "Vendor Ltd",
    "createdDateTime": "2020-03-02T03:04:05Z",
    "lastModifiedDateTime": "2020-03-02T03:04:05Z",
}

#: A child folder's display name is what the folder chain is rebuilt from on import.
_VENDORS_FOLDER = {"id": "f2", "displayName": "Vendors"}


def _transport(contacts=None, child_folders=None, children=None) -> MethodRoutingTransport:
    return MethodRoutingTransport(
        [
            # Deeper routes first: a child folder's URL nests under its parent's.
            (
                None,
                "/contactFolders/f1/childFolders/f2/contacts?",
                {"value": children if children is not None else [_VENDOR]},
            ),
            (None, "/contactFolders/f1/childFolders/f2/childFolders", {"value": []}),
            (
                None,
                "/contactFolders/f1/contacts?",
                {"value": contacts if contacts is not None else [_ALICE, _MINIMAL]},
            ),
            (
                None,
                "/contactFolders/f1/childFolders",
                {"value": child_folders if child_folders is not None else [_VENDORS_FOLDER]},
            ),
            (None, "/contactFolders/f1", _FOLDER),
        ]
    )


def _client(transport: MethodRoutingTransport) -> GraphClient:
    client = GraphClient()
    client.pending_request().beforeExecute.clear()
    client.pending_request().transport = transport
    return client


def _folder(client: GraphClient):
    return client.me.contact_folders["f1"].get().execute_query()


def _digest(value: str) -> str:
    return hashlib.sha1(value.encode("utf-8")).hexdigest()[:8]


def _source() -> ContactSource:
    return ContactSource(_folder(_client(_transport())))


# -- the source ----------------------------------------------------------------


def test_source_enumerates_one_item_per_contact_and_subfolder():
    items = _source().list_items()

    assert [item.dest_path for item in items] == [
        f"Contacts/Alice-Example_{_digest('c1')}.vcf",
        f"Contacts/Bob-Example_{_digest('c2')}.vcf",
        f"Contacts/Vendors/Vendor-Ltd_{_digest('c3')}.vcf",
    ]
    assert all(item.item_type == "contact" for item in items)


def test_source_can_leave_the_subfolders_out():
    transport = _transport()
    items = ContactSource(_folder(_client(transport)), ContactExportOptions(include_subfolders=False)).list_items()

    assert [item.dest_path for item in items] == [
        f"Contacts/Alice-Example_{_digest('c1')}.vcf",
        f"Contacts/Bob-Example_{_digest('c2')}.vcf",
    ]


def test_source_names_the_root_from_the_options():
    transport = _transport()
    items = ContactSource(_folder(_client(transport)), ContactExportOptions(root_name="mbox")).list_items()

    assert items[0].dest_path == f"mbox/Alice-Example_{_digest('c1')}.vcf"
    assert items[2].dest_path == f"mbox/Vendors/Vendor-Ltd_{_digest('c3')}.vcf"


def test_source_records_the_envelope_an_import_replays():
    item = _source().list_items()[0]
    envelope = item.metadata

    assert item.source_id == "c1"
    assert envelope["display_name"] == "Alice Example"
    assert envelope["given_name"] == "Alice"
    assert envelope["file_as"] == "Example, Alice"
    assert envelope["job_title"] == "Controller"
    assert envelope["business_phones"] == ["+1 555 0100", "+1 555 0101"]
    assert envelope["email_addresses"] == [
        {"name": "Alice Example", "address": "alice@contoso.com"},
        {"name": "alice@contoso.example", "address": "alice@contoso.example"},
    ]
    assert envelope["categories"] == ["Finance", "Board, quarterly"]
    # The typed ``PhysicalAddress`` is flattened: a repr would be unreadable on import.
    assert envelope["business_address"] == {
        "street": "1 Main St",
        "city": "Springfield",
        "state": "IL",
        "postal_code": "62701",
        "country_or_region": "USA",
    }
    assert envelope["other_address"] == {
        "street": None,
        "city": "Kyiv",
        "state": None,
        "postal_code": None,
        "country_or_region": None,
    }
    assert envelope["birthday"] == "1953-05-01T11:59:00+00:00"
    assert envelope["vcf_path"] == item.dest_path
    assert envelope["folder_display_path"] == "Contacts"
    assert item.created == "2020-01-02T03:04:05+00:00"
    assert item.modified == "2021-02-03T04:05:06+00:00"


def test_source_translates_a_child_folder_display_path():
    item = _source().list_items()[2]

    assert item.metadata["folder_path"] == "Contacts/Vendors"
    assert item.metadata["folder_display_path"] == "Contacts/Vendors"


def test_source_envelope_is_json_safe():
    """Nothing may be rescued by ``default=str``: a nested wrapper would poison the sidecar."""
    for item in _source().list_items():
        json.dumps(item.metadata)


def test_source_checksum_is_the_vcard_bytes_this_product_renders():
    source = _source()
    item = source.list_items()[0]

    assert source.checksum(item) == hashlib.md5(contact_vcard(item.metadata)).hexdigest()


def test_the_projection_asks_for_the_fields_the_envelope_records():
    assert "birthday" in CONTACT_COLUMNS
    assert "businessAddress" in CONTACT_COLUMNS
    assert "emailAddresses" in CONTACT_COLUMNS
    # ``hasPhoto`` is deliberately absent: the endpoint does not answer it (measured).
    assert "hasPhoto" not in CONTACT_COLUMNS


def test_the_export_projection_is_the_model_projection():
    """``CONTACT_COLUMNS`` is derived from the model, not kept beside it.

    A hand-kept list drifts from the getters that consume it, and a ``$select`` that
    omits a column is indistinguishable from a contact that has no value for it —
    which is how the calendar projection silently lost ``isCancelled``.
    """
    assert CONTACT_COLUMNS == Contact.select_all()
    assert not set(CONTACT_COLUMNS) & set(Contact.expandable())


# -- the vCard document --------------------------------------------------------


def test_vcard_carries_the_identity_and_the_org():
    data = _source().read(_source().list_items()[0]).decode("utf-8")
    lines = data.split("\r\n")

    assert lines[0] == "BEGIN:VCARD"
    assert lines[1] == "VERSION:3.0"
    assert "N:Example;Alice;B;Dr.;Jr." in lines
    assert "FN:Alice Example" in lines
    assert "ORG:Contoso;Finance" in lines
    assert "TITLE:Controller" in lines
    assert "ROLE:Accountant" in lines
    assert "UID:c1" in lines


def test_vcard_carries_the_phones_addresses_and_birthday():
    data = _source().read(_source().list_items()[0]).decode("utf-8")

    assert "TEL;TYPE=WORK,VOICE:+1 555 0100" in data
    assert "TEL;TYPE=HOME,VOICE:+1 555 0199" in data
    assert "TEL;TYPE=CELL:+1 555 0150" in data
    assert "EMAIL;TYPE=INTERNET:alice@contoso.com" in data
    assert "ADR;TYPE=WORK:;;1 Main St;Springfield;IL;62701;USA" in data
    assert "ADR;TYPE=OTHER:;;;Kyiv;;;" in data
    assert "BDAY:1953-05-01" in data
    assert "REV:20210203040506Z" in data


def test_vcard_escapes_the_text_values():
    data = _source().read(_source().list_items()[0]).decode("utf-8")

    # Newlines become ``\n``; a comma inside a category is escaped, the separator is not.
    assert "NOTE:Line one\\nLine two\\; with comma\\, and semicolon" in data
    assert "CATEGORIES:Finance,Board\\, quarterly" in data


def test_vcard_lines_are_folded_at_75_octets_and_use_crlf():
    notes = "x" * 200
    transport = _transport(contacts=[{**_MINIMAL, "personalNotes": notes}], child_folders=[])
    data = ContactSource(_folder(_client(transport))).read(ContactSource(_folder(_client(transport))).list_items()[0])

    assert b"\r\n" in data
    for line in data.split(b"\r\n"):
        assert len(line) <= 75  # noqa: PLR2004 — RFC 6350 §3.1 octet cap
    assert notes.encode() not in data


# -- the target ----------------------------------------------------------------


def test_export_writes_a_vcf_a_sidecar_and_a_manifest(tmp_path: Path):
    job = MigrationJob(_source(), VcfExportTarget(tmp_path))

    job.plan()
    stats = job.run()

    assert stats.success == 3  # noqa: PLR2004 — two contacts and the subfolder's one
    written = sorted(path.name for path in (tmp_path / "Contacts").iterdir())
    assert written == [
        f"Alice-Example_{_digest('c1')}.json",
        f"Alice-Example_{_digest('c1')}.vcf",
        f"Bob-Example_{_digest('c2')}.json",
        f"Bob-Example_{_digest('c2')}.vcf",
        "Vendors",
    ]
    assert (tmp_path / "Contacts" / "Vendors" / f"Vendor-Ltd_{_digest('c3')}.vcf").exists()
    manifest = (tmp_path / MANIFEST_NAME).read_text(encoding="utf-8").splitlines()
    assert len(manifest) == 3  # noqa: PLR2004 — one sidecar record per contact
    assert json.loads(manifest[0])["display_name"] == "Alice Example"


def test_export_preserves_the_contact_digest_round_trip(tmp_path: Path):
    """An exported contact's digest is what the import will be verified against."""
    job = MigrationJob(_source(), VcfExportTarget(tmp_path))
    job.plan()
    job.run()

    wanted = f"Alice-Example_{_digest('c1')}.vcf"
    item = next(item for item in job.source.list_items() if item.dest_path.endswith(wanted))
    sidecar = json.loads((tmp_path / item.dest_path).with_suffix(".json").read_text(encoding="utf-8"))

    assert contact_digest(sidecar) == contact_digest(item.metadata)


def test_export_verifies_the_bytes_it_rendered(tmp_path: Path):
    """The ``.vcf`` is ours, so byte equality across the tree is fair here."""
    job = MigrationJob(_source(), VcfExportTarget(tmp_path))
    job.plan()
    job.run()

    report = job.verify()

    assert (report.checked, report.mismatches) == (3, [])


def test_export_skips_a_re_run(tmp_path: Path):
    job = MigrationJob(_source(), VcfExportTarget(tmp_path))
    job.plan()
    job.run()

    again = MigrationJob(_source(), VcfExportTarget(tmp_path))
    again.plan()
    stats = again.run()

    assert (stats.success, stats.skipped) == (0, 3)
