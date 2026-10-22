"""Contact import: a vCard sidecar tree as the source, a Graph contact folder as the target.

The transport scripts Exchange the way it answers: a ``POST /contacts`` that echoes the
contact it created (assigning an id and the timestamps, renaming an address-only email
entry after its address, and rewriting a birthday to its fixed ``11:59``), a folder
listing used to recognise what an earlier run already created, and a read that hands
the contact back. Those three rewrites are measured live, and each one is why the
digest normalises the way it does.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest
from office365.graph_client import GraphClient
from office365.migration import MigrationJob
from office365.migration.base import MigrationItem
from office365.migration.outlook import (
    ContactImportOptions,
    ContactRecord,
    ContactTarget,
    VcfTreeSource,
)
from office365.migration.outlook.contacts_models import _RESTORED, CONTACT_COLUMNS
from office365.outlook.contacts.contact import Contact
from tests._scripted_transport import MethodRoutingTransport


def _verb(request) -> str:
    """The HTTP verb as a plain string (``HttpMethod.Post`` -> ``"POST"``)."""
    return str(getattr(request.method, "value", request.method)).upper()


_FOLDER = {"id": "f1", "displayName": "Imported contacts"}


def _record(**overrides: Any) -> ContactRecord:
    """The record a sidecar with these fields holds (no client, no context)."""
    return ContactRecord.from_json(_envelope(**overrides))


def _envelope(**overrides: Any) -> dict[str, Any]:
    envelope: dict[str, Any] = {
        "id": "c1",
        "folder_path": "Contacts",
        "folder_display_path": "Contacts",
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
        "personalNotes": "Line one\nLine two",
        "spouseName": "Sam Example",
        "children": ["Kim"],
        "imAddresses": ["sip:alice@contoso.com"],
        "businessPhones": ["+1 555 0100"],
        "homePhones": ["+1 555 0199"],
        "mobilePhone": "+1 555 0150",
        "emailAddresses": [
            {"name": "Alice Example", "address": "alice@contoso.com"},
            {"name": "alice@contoso.example", "address": "alice@contoso.example"},
        ],
        "categories": ["Finance", "Board quarterly"],
        "createdDateTime": "2020-01-02T03:04:05+00:00",
        "lastModifiedDateTime": "2021-02-03T04:05:06+00:00",
        "businessAddress": {
            "street": "1 Main St",
            "city": "Springfield",
            "state": "IL",
            "postalCode": "62701",
            "countryOrRegion": "USA",
        },
        "homeAddress": {},
        "otherAddress": {"city": "Kyiv", "countryOrRegion": "Ukraine"},
        "vcf_path": "Contacts/Alice-Example_c1.vcf",
    }
    envelope.update(overrides)
    return envelope


#: A source duplicate: same display name and same address, which the import must honour.
_TWIN = _envelope(id="c2", fileAs="Twin, Alice", vcf_path="Contacts/Alice-Example-twin_c2.vcf")

_MINIMAL = {
    "id": "c3",
    "folder_path": "Contacts",
    "folder_display_path": "Contacts",
    "displayName": "Bob Example",
    "emailAddresses": [{"address": "bob@contoso.com"}],
    "vcf_path": "Contacts/Bob-Example_c3.vcf",
}

#: A contact under the export root's child folder.
_NESTED = _envelope(
    id="c4",
    folder_path="Contacts/Vendors",
    folder_display_path="Contacts/Vendors",
    displayName="Vendor Ltd",
    emailAddresses=[],
    vcf_path="Contacts/Vendors/Vendor-Ltd_c4.vcf",
)


class _Store:
    """A fake Exchange contact folder tree: create, folder chain, listing and read-back."""

    def __init__(self, contacts: list[dict[str, Any]] | None = None) -> None:
        self.contacts: dict[str, dict[str, Any]] = {contact["id"]: dict(contact) for contact in contacts or []}
        self.owners: dict[str, str] = {contact["id"]: "f1" for contact in contacts or []}
        self.posted: list[dict[str, Any]] = []
        self.folders: list[tuple[str, str, str]] = []  # (id, parent id, display name)
        #: Contacts an earlier listing hid — a concurrent run creating one mid-import.
        self.hidden: set[str] = set()

    def routes(self):
        # Deeper routes first: ``/contacts/c1`` also contains ``/contacts``.
        return [
            (None, "/contacts/c", self._read),
            ("POST", "/contacts", self._create),
            (None, "/contacts?", self._listing),
            (None, "/childFolders", self._folder),
            (None, "/contactFolders/f1", _FOLDER),
        ]

    def _folder_of(self, url: str) -> str:
        """The folder a URL addresses — the deepest ``childFolders`` id, else the root."""
        base = url.split("?", maxsplit=1)[0].removesuffix("/childFolders")
        if "/childFolders/" in base:
            return base.rsplit("/childFolders/", 1)[1].split("/")[0]
        return "f1"

    def _folder(self, request):
        """``ensure()`` creates first and falls back to a filtered read on a duplicate."""
        parent = self._folder_of(request.url)
        if _verb(request) == "POST":
            name = request.data["displayName"]
            folder_id = f"f{len(self.folders) + 2}"
            self.folders.append((folder_id, parent, name))
            return {"id": folder_id, "displayName": name}
        return {
            "value": [
                {"id": folder_id, "displayName": name} for folder_id, owner, name in self.folders if owner == parent
            ]
        }

    def _listing(self, request):
        folder_id = self._folder_of(request.url)
        return {
            "value": [
                {
                    "id": contact["id"],
                    "displayName": contact.get("displayName"),
                    "emailAddresses": contact.get("emailAddresses") or [],
                }
                for contact in self.contacts.values()
                if self.owners[contact["id"]] == folder_id and contact["id"] not in self.hidden
            ]
        }

    def _read(self, request):
        return self.contacts[request.url.split("/contacts/")[1].split("?")[0]]

    def _create(self, request):
        payload = request.data
        if isinstance(payload, str):
            payload = json.loads(payload)
        self.posted.append(payload)
        created = self._as_returned(payload, f"c{len(self.contacts) + 10}")
        self.contacts[created["id"]] = created
        self.owners[created["id"]] = self._folder_of(request.url)
        return created

    @staticmethod
    def _as_returned(payload: dict[str, Any], contact_id: str) -> dict[str, Any]:
        """What Exchange hands back for a created contact: the payload plus its own rewrites."""
        emails = [
            {"address": entry["address"], "name": entry.get("name") or entry["address"]}
            for entry in payload.get("emailAddresses") or []
        ]
        return {
            **payload,
            "id": contact_id,
            "emailAddresses": emails,
            # Measured: a birthday is stored at a fixed 11:59 whatever time of day was sent.
            "birthday": "1953-05-01T11:59:00+00:00" if payload.get("birthday") else None,
            "createdDateTime": "2026-03-02T12:00:00Z",
            "lastModifiedDateTime": "2026-03-02T12:00:00Z",
        }


def _client(store: _Store) -> GraphClient:
    client = GraphClient()
    client.pending_request().beforeExecute.clear()
    client.pending_request().transport = MethodRoutingTransport(store.routes())
    return client


def _target(store: _Store, options: ContactImportOptions | None = None) -> ContactTarget:
    return ContactTarget(_client(store).me.contact_folders["f1"].get().execute_query(), options)


def _tree(root: Path, envelopes: dict[str, dict[str, Any]]) -> Path:
    """Write an exported contact tree: a ``.vcf`` plus the sidecar the export records."""
    for relative, envelope in envelopes.items():
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(b"BEGIN:VCARD\r\nEND:VCARD\r\n")
        path.with_suffix(".json").write_text(json.dumps(envelope), encoding="utf-8")
    return root


def _root(tmp_path: Path, envelopes: dict[str, dict[str, Any]] | None = None) -> Path:
    return _tree(tmp_path / "export", envelopes or {"Contacts/Alice-Example_c1.vcf": _envelope()})


# -- the source ----------------------------------------------------------------


def test_source_reads_the_sidecar_tree(tmp_path: Path):
    items = VcfTreeSource(
        _root(
            tmp_path,
            {"Contacts/Alice-Example_c1.vcf": _envelope(), "Contacts/Vendors/Vendor-Ltd_c4.vcf": _NESTED},
        )
    ).list_items()

    assert [item.dest_path for item in items] == ["Contacts/Alice-Example_c1.vcf", "Contacts/Vendors/Vendor-Ltd_c4.vcf"]
    assert all(item.item_type == "contact" for item in items)
    assert items[0].metadata["displayName"] == "Alice Example"
    assert items[1].metadata["folder_display_path"] == "Contacts/Vendors"
    assert items[0].source_id == "c1"


def test_source_checksum_is_the_digest_the_target_can_compute(tmp_path: Path):
    item = VcfTreeSource(_root(tmp_path)).list_items()[0]

    assert VcfTreeSource(_root(tmp_path)).checksum(item) == _record().digest()


def test_source_refuses_a_vcf_without_a_sidecar(tmp_path: Path):
    root = _root(tmp_path)
    (root / "Contacts" / "Alice-Example_c1.json").unlink()

    with pytest.raises(FileNotFoundError, match="the sidecar is the import contract"):
        VcfTreeSource(root).list_items()


def test_source_refuses_a_sidecar_that_escapes_the_tree(tmp_path: Path):
    source = VcfTreeSource(_root(tmp_path))
    item = MigrationItem("../../etc/passwd.vcf", "../../etc/passwd.vcf", 0, "contact")

    with pytest.raises(ValueError, match="escapes the export tree"):
        source.read(item)


def test_source_refuses_a_directory_that_is_not_an_export(tmp_path: Path):
    with pytest.raises(FileNotFoundError, match="is not a directory of exported .vcf files"):
        VcfTreeSource(tmp_path / "nope").list_items()


# -- the payload ---------------------------------------------------------------


def test_payload_carries_the_contact_fields_an_import_restores():
    payload = _record().payload()

    assert payload["displayName"] == "Alice Example"
    assert (payload["givenName"], payload["surname"]) == ("Alice", "Example")
    assert payload["jobTitle"] == "Controller"
    assert payload["businessHomePage"] == "https://contoso.example/alice"
    assert payload["businessPhones"] == ["+1 555 0100"]
    assert payload["homePhones"] == ["+1 555 0199"]
    assert payload["mobilePhone"] == "+1 555 0150"
    assert payload["imAddresses"] == ["sip:alice@contoso.com"]
    assert payload["children"] == ["Kim"]
    assert payload["categories"] == ["Finance", "Board quarterly"]
    assert payload["businessAddress"] == {
        "street": "1 Main St",
        "city": "Springfield",
        "state": "IL",
        "postalCode": "62701",
        "countryOrRegion": "USA",
    }
    # Server-owned: sending them back is at best ignored. This is a reading of the model's
    # own statement (``@odata(readonly=True)``), not a second copy of it.
    for owned in (
        "id",
        "createdDateTime",
        "lastModifiedDateTime",
        "changeKey",
        "parentFolderId",
        "primaryEmailAddress",
    ):
        assert owned not in payload, owned
        assert owned in Contact._schema.readonly, owned


def test_the_replay_set_is_the_model_s_projection_of_what_the_service_does_not_own():
    """The replay set is derived, not kept beside the model.

    A partition rather than a list: the columns the model marks readonly and the columns an
    import replays add up to every column the export selects, with no overlap — so a column
    the model gains is exported, replayed and verified without this module changing, and a
    column the model marks readonly cannot quietly stay in the replay set.
    """
    owned = Contact._schema.readonly & frozenset(CONTACT_COLUMNS)

    assert owned == frozenset(
        {
            "id",
            "changeKey",
            "createdDateTime",
            "lastModifiedDateTime",
            "parentFolderId",
            "primaryEmailAddress",
        }
    )
    assert owned | _RESTORED == frozenset(CONTACT_COLUMNS), "a column is neither replayed nor owned"
    assert not owned & _RESTORED, "a column is both replayed and owned"


def test_payload_posts_an_email_entry_as_the_sidecar_holds_it():
    """An address-only entry stays address-only: Exchange fills the name, the digest allows for it."""
    payload = ContactRecord.from_json(_MINIMAL).payload()

    assert payload["emailAddresses"] == [{"address": "bob@contoso.com"}]


def test_payload_posts_a_declared_column_it_was_never_told_about():
    """A contact field the model declares is replayed without this module naming it."""
    payload = _record(yomiGivenName="Arisu").payload()

    assert payload["yomiGivenName"] == "Arisu"


def test_the_digest_follows_a_declared_column_it_was_never_told_about():
    """The same field therefore also takes part in verification."""
    assert _record(yomiGivenName="Arisu").digest() != _record().digest()


def test_payload_refuses_a_category_that_carries_a_comma():
    # Measured live: Exchange answers ErrorPropertyUpdate ("Property update did not
    # succeed.") to a whole contact when one category holds a comma, so the refusal
    # names the category instead of failing opaquely at the server.
    with pytest.raises(ValueError) as exc:
        _record(categories=["Board, quarterly"]).payload()

    assert "Board, quarterly" in str(exc.value)
    assert "comma" in str(exc.value)


def test_payload_drops_categories_unless_asked():
    payload = _record().payload(ContactImportOptions(restore_categories=False))

    assert "categories" not in payload


def test_payload_refuses_a_contact_without_a_display_name():
    with pytest.raises(ValueError, match="no display name"):
        _record(displayName="  ").payload()


# -- the digest ----------------------------------------------------------------


def test_a_birthday_compares_by_date_because_exchange_rewrites_the_time():
    """Measured: ``T00:00:00Z`` and ``T11:59:00+00:00`` both come back as 11:59."""
    midnight = _envelope(birthday="1953-05-01T00:00:00Z")
    noon = _envelope(birthday="1953-05-01T11:59:00+00:00")

    assert ContactRecord.from_json(midnight).digest() == ContactRecord.from_json(noon).digest()
    assert _record(birthday="1953-05-02T00:00:00Z").digest() != ContactRecord.from_json(noon).digest()


def test_an_email_compares_as_address_and_name_or_address():
    named = _envelope(emailAddresses=[{"name": "Alice", "address": "alice@contoso.com"}])
    unnamed = _envelope(emailAddresses=[{"address": "alice@contoso.com"}])
    filled = _envelope(emailAddresses=[{"name": "alice@contoso.com", "address": "alice@contoso.com"}])

    # Exchange fills in the address as the name, so `None` and the filled-in form agree…
    assert ContactRecord.from_json(unnamed).digest() == ContactRecord.from_json(filled).digest()
    # …but a real name is a different contact record.
    assert ContactRecord.from_json(named).digest() != ContactRecord.from_json(unnamed).digest()


def test_the_digest_ignores_server_owned_fields():
    owned = _envelope(id="c9", createdDateTime=None, lastModifiedDateTime=None, vcf_path="x.vcf")

    assert ContactRecord.from_json(owned).digest() == _record().digest()


def test_the_digest_follows_the_categories_option():
    dropped = ContactImportOptions(restore_categories=False)

    assert _record(categories=[]).digest(dropped) == _record().digest(dropped)
    assert _record(categories=[]).digest() != _record().digest()


def test_the_dedup_key_is_the_name_and_the_first_address():
    assert _record().dedup_key == ("alice example", "alice@contoso.com")
    assert ContactRecord.from_json(_MINIMAL).dedup_key == ("bob example", "bob@contoso.com")
    # No address left: the name alone is all there is to recognise it by.
    assert ContactRecord.from_json(_NESTED).dedup_key == ("vendor ltd", "")


# -- the target ----------------------------------------------------------------


def test_import_creates_the_contact_from_the_sidecar(tmp_path: Path):
    store = _Store()
    job = MigrationJob(VcfTreeSource(_root(tmp_path)), _target(store))

    job.plan()
    stats = job.run()

    assert stats.success == 1
    assert store.posted[0]["displayName"] == "Alice Example"
    assert store.posted[0]["businessAddress"]["postalCode"] == "62701"


def test_import_verifies_the_contact_across_the_server_rewrites(tmp_path: Path):
    store = _Store()
    job = MigrationJob(VcfTreeSource(_root(tmp_path)), _target(store))

    job.plan()
    job.run()
    report = job.verify()

    assert (report.checked, report.mismatches) == (1, [])


def test_import_reports_a_field_that_did_not_arrive(tmp_path: Path):
    store = _Store()
    job = MigrationJob(VcfTreeSource(_root(tmp_path)), _target(store))
    job.plan()
    job.run()
    store.contacts["c10"]["jobTitle"] = "Something else"  # noqa: PLR2004 — the id the fake assigned

    report = job.verify()

    assert report.checked == 1
    assert len(report.mismatches) == 1


def test_import_skips_what_an_earlier_run_created(tmp_path: Path):
    first = _Store()
    job = MigrationJob(VcfTreeSource(_root(tmp_path)), _target(first))
    job.plan()
    job.run()

    second = _Store(list(first.contacts.values()))
    again = MigrationJob(VcfTreeSource(_root(tmp_path)), _target(second))
    again.plan()
    stats = again.run()

    assert (stats.success, stats.skipped) == (0, 1)
    assert second.posted == []


def test_import_honours_duplicates_at_the_source(tmp_path: Path):
    """Two contacts sharing a name and address are two contacts, not one to collapse."""
    store = _Store()
    root = _root(tmp_path, {"Contacts/Alice-Example_c1.vcf": _envelope(), "Contacts/twin_c2.vcf": _TWIN})
    job = MigrationJob(VcfTreeSource(root), _target(store))

    job.plan()
    stats = job.run()

    assert stats.success == 2  # noqa: PLR2004 — the twin is imported too
    assert [payload["fileAs"] for payload in store.posted] == ["Example, Alice", "Twin, Alice"]


def test_import_recreates_the_subfolder_chain(tmp_path: Path):
    store = _Store()
    root = _root(
        tmp_path,
        {"Contacts/Alice-Example_c1.vcf": _envelope(), "Contacts/Vendors/Vendor-Ltd_c4.vcf": _NESTED},
    )
    job = MigrationJob(VcfTreeSource(root), _target(store))

    job.plan()
    job.run()

    # The root directory of the export is the target folder itself, so only ``Vendors``
    # is a real child — it is created through the folder collection's idempotent ensure.
    assert [(parent, name) for _, parent, name in store.folders] == [("f1", "Vendors")]
    assert [payload["displayName"] for payload in store.posted] == ["Alice Example", "Vendor Ltd"]
    assert store.owners[store.posted and "c11"] == "f2"  # the vendor landed in its own folder


def test_import_reports_the_categories_it_left_off(tmp_path: Path):
    store = _Store()
    options = ContactImportOptions(restore_categories=False)
    root = _root(tmp_path, {"Contacts/Alice-Example_c1.vcf": _envelope(categories=["Finance"])})
    job = MigrationJob(VcfTreeSource(root, options), _target(store, options))

    job.plan()
    job.run()
    job.target.commit()

    assert "categories were left off 1 contact(s)" in job.target.warnings[0]
    assert "restore_categories=False" in job.target.warnings[0]


def test_import_refuses_a_payload_that_is_not_a_contact(tmp_path: Path):
    target = _target(_Store())

    with pytest.raises(ValueError, match="a contact folder imports contacts, not 'event'"):
        target.write(MigrationItem("a.vcf", "a.vcf", 0, "event", metadata=_envelope()), b"")


def test_import_refuses_a_sidecar_the_service_would_reject(tmp_path: Path):
    store = _Store()
    root = _root(tmp_path, {"Contacts/nameless_c1.vcf": _envelope(displayName=None)})
    job = MigrationJob(VcfTreeSource(root), _target(store))

    job.plan()
    stats = job.run()

    assert (stats.success, stats.errors) == (0, 1)
    assert store.posted == []
