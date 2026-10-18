"""Mail export: a Graph folder as a source, an EML tree as the target (offline).

The transport scripts Graph the way the service answers: one page of messages per
folder, a folder tree of `childFolders`, and RFC 822 bytes on `/$value`.
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

from office365.graph_client import GraphClient
from office365.migration import MigrationJob
from office365.migration.outlook import (
    MANIFEST_NAME,
    MailExportOptions,
    MailExportTarget,
    MailFolderSource,
    mail_slug,
)
from office365.migration.outlook.models import MAX_SLUG_LENGTH
from tests._scripted_transport import MethodRoutingTransport

_INBOX = [
    {
        "id": "m1",
        "internetMessageId": "<m1@contoso.com>",
        "subject": "Quarterly report: Q1",
        "receivedDateTime": "2024-03-01T09:15:00Z",
        "sentDateTime": "2024-03-01T09:14:00Z",
        "lastModifiedDateTime": "2024-03-01T09:16:00Z",
        "isRead": True,
        "isDraft": False,
        "importance": "normal",
        "categories": ["Finance", "Q1"],
        "hasAttachments": True,
        "conversationId": "c1",
        "parentFolderId": "inbox",
        "from": {"emailAddress": {"name": "Alice", "address": "alice@contoso.com"}},
        "toRecipients": [{"emailAddress": {"name": "Bob", "address": "bob@contoso.com"}}],
        "ccRecipients": [],
    },
    {
        "id": "m2",
        "internetMessageId": "<m2@contoso.com>",
        "subject": "Quarterly report: Q1",  # same subject and day as m1
        "receivedDateTime": "2024-03-01T10:00:00Z",
        "isRead": False,
        "isDraft": False,
        "categories": [],
        "hasAttachments": False,
        "parentFolderId": "inbox",
        "from": {"emailAddress": {"address": "carol@contoso.com"}},
        "toRecipients": [],
        "ccRecipients": [],
    },
    {
        "id": "draft1",
        "subject": "unsent — ünïcode/日記",  # no internetMessageId: keyed by Graph id
        "receivedDateTime": "2024-03-02T08:00:00Z",
        "isRead": True,
        "isDraft": True,
        "categories": [],
        "hasAttachments": False,
        "parentFolderId": "inbox",
        "from": {"emailAddress": {"address": "alice@contoso.com"}},
        "toRecipients": [],
        "ccRecipients": [],
    },
]

_ARCHIVE = [
    {
        "id": "m3",
        "internetMessageId": "<m3@contoso.com>",
        "subject": "Old thread",
        "receivedDateTime": "2023-12-24T18:30:00Z",
        "isRead": True,
        "isDraft": False,
        "categories": [],
        "hasAttachments": False,
        "parentFolderId": "archive",
        "from": {"emailAddress": {"address": "dave@contoso.com"}},
        "toRecipients": [],
        "ccRecipients": [],
    }
]

_MIME = {
    "m1": b"From: Alice <alice@contoso.com>\r\nSubject: Quarterly report: Q1\r\n\r\nbody-1\r\n",
    "m2": b"From: Carol <carol@contoso.com>\r\nSubject: Quarterly report: Q1\r\n\r\nbody-2\r\n",
    "draft1": b"From: alice@contoso.com\r\nSubject: unsent\r\n\r\nbody-draft\r\n",
    "m3": b"From: Dave <dave@contoso.com>\r\nSubject: Old thread\r\n\r\nbody-3\r\n",
}

_M1_SIZE = len(_MIME["m1"])  # the transported byte count: Exchange does not expose `size`
_INBOX_FOLDER = {"id": "inbox", "displayName": "Inbox", "totalItemCount": 3, "childFolderCount": 1}
_ARCHIVE_FOLDER = {"id": "archive", "displayName": "Archive", "totalItemCount": 1, "childFolderCount": 0}


def _mime_for(request) -> bytes:
    for message_id, body in _MIME.items():
        if f"/messages/{message_id}/$value" in request.url:
            return body
    raise AssertionError(f"no MIME scripted for {request.url}")


def _transport(routes=None) -> MethodRoutingTransport:
    return MethodRoutingTransport(
        routes
        if routes is not None
        else [
            (None, "/$value", _mime_for),
            # A nested folder's collections hang off the parent's ``childFolders``
            # navigation (that is how Graph addresses them), so the deeper routes
            # have to be matched before the shallower ones.
            (None, "/childFolders/archive/childFolders", {"value": []}),
            (None, "/childFolders/archive/messages", {"value": _ARCHIVE}),
            (None, "/mailFolders/inbox/childFolders", {"value": [_ARCHIVE_FOLDER]}),
            (None, "/mailFolders/inbox/messages", {"value": _INBOX}),
            (None, "/mailFolders/inbox", _INBOX_FOLDER),
        ]
    )


def _client(transport: MethodRoutingTransport) -> GraphClient:
    client = GraphClient()
    client.pending_request().beforeExecute.clear()
    client.pending_request().transport = transport
    return client


def _folder(client: GraphClient):
    return client.me.mail_folders["inbox"].get().execute_query()


def test_source_enumerates_a_folder_tree_into_eml_items():
    client = _client(_transport())
    source = MailFolderSource(_folder(client))

    items = source.list_items()

    assert [item.dest_path for item in items] == [
        "Inbox/2024-03-01_Quarterly-report-Q1_" + hashlib.sha1(b"<m1@contoso.com>").hexdigest()[:8] + ".eml",
        "Inbox/2024-03-01_Quarterly-report-Q1_" + hashlib.sha1(b"<m2@contoso.com>").hexdigest()[:8] + ".eml",
        "Inbox/2024-03-02_unsent-unicode_" + hashlib.sha1(b"draft1").hexdigest()[:8] + ".eml",
        "Inbox/Archive/2023-12-24_Old-thread_" + hashlib.sha1(b"<m3@contoso.com>").hexdigest()[:8] + ".eml",
    ]
    assert all(item.item_type == "file" for item in items)
    # Same subject and day: the id digest is what keeps the two paths apart.
    assert items[0].dest_path != items[1].dest_path


def test_source_records_the_envelope_that_mime_cannot_carry():
    client = _client(_transport())
    source = MailFolderSource(_folder(client))

    first = source.list_items()[0]

    assert first.source_id == "<m1@contoso.com>"
    assert first.metadata["subject"] == "Quarterly report: Q1"
    assert first.metadata["sender"] == "Alice <alice@contoso.com>"
    assert first.metadata["to"] == ["Bob <bob@contoso.com>"]
    assert first.metadata["categories"] == ["Finance", "Q1"]
    assert first.metadata["is_read"] is True
    assert first.metadata["conversation_id"] == "c1"
    assert first.metadata["eml_path"] == first.dest_path
    assert first.created == "2024-03-01T09:15:00+00:00"
    # Exchange will not project `size`, so the plan carries no byte count...
    assert first.size_bytes == 0
    # ...and the size is filled in from the MIME that is actually transferred.
    assert len(source.read(first)) == _M1_SIZE
    assert first.size_bytes == _M1_SIZE


def test_source_projects_every_property_it_reads():
    """One projection: a field the envelope records must be in the `$select`."""
    transport = _transport()
    client = _client(transport)

    MailFolderSource(_folder(client)).list_items()

    url = next(request.url for request in transport.requests if "/messages?" in request.url)
    for column in ("internetMessageId", "receivedDateTime", "lastModifiedDateTime", "categories"):
        assert column in url, column


def test_source_does_not_project_a_column_the_backend_rejects():
    """`message.size` is documented but not selectable on the Exchange backend.

    ``$select=size`` answers ``RequestBroker--ParseUri: Could not find a property named
    'size' on type 'Microsoft.OutlookServices.Message'``, so an export that asked for it
    failed on the first folder. The transported byte count is filled in by ``read()``.
    """
    transport = _transport()
    client = _client(transport)

    MailFolderSource(_folder(client)).list_items()

    url = next(request.url for request in transport.requests if "/messages?" in request.url)
    assert "size" not in url


def test_source_reads_rfc822_bytes_and_checksums_them():
    client = _client(_transport())
    source = MailFolderSource(_folder(client))
    items = source.list_items()

    payload = source.read(items[0])

    assert payload == _MIME["m1"]
    assert source.checksum(items[0]) == hashlib.md5(_MIME["m1"]).hexdigest()  # noqa: S324 - the toolkit's checksum


def test_source_can_skip_subfolders_and_drafts():
    client = _client(_transport())
    flat = MailFolderSource(_folder(client), MailExportOptions(include_subfolders=False, include_drafts=False))

    items = flat.list_items()

    assert [item.metadata["graph_id"] for item in items] == ["m1", "m2"]


def test_source_resolves_items_when_the_plan_came_from_disk():
    client = _client(_transport())
    source = MailFolderSource(_folder(client))
    planned = source.list_items()[0]

    # A second instance has no handles: reading an item re-enumerates once.
    fresh = MailFolderSource(_folder(client))

    assert fresh.read(planned) == _MIME["m1"]


def test_dest_paths_are_safe_and_bounded():
    assert mail_slug('a/b\\c:d*e?f"g<h>i|j') == "a-b-c-d-e-f-g-h-i-j"
    assert mail_slug("Über 日本語 report") == "Uber-report"
    assert len(mail_slug("x" * 500)) == MAX_SLUG_LENGTH
    assert mail_slug(None) == ""


def test_target_writes_eml_a_sidecar_and_the_index(tmp_path: Path):
    client = _client(_transport())
    source = MailFolderSource(_folder(client))
    items = source.list_items()
    target = MailExportTarget(tmp_path)

    for item in items:
        target.write(item, source.read(item))
    target.commit()

    assert sorted(target.list_paths()) == sorted(item.dest_path for item in items)  # .eml only
    eml = tmp_path / items[0].dest_path
    assert eml.read_bytes() == _MIME["m1"]
    sidecar = json.loads(eml.with_suffix(".json").read_text())
    assert sidecar["categories"] == ["Finance", "Q1"]
    assert sidecar["eml_path"] == items[0].dest_path
    index = [json.loads(line) for line in (tmp_path / MANIFEST_NAME).read_text().splitlines()]
    assert {record["eml_path"] for record in index} == set(target.list_paths())


def test_target_reads_back_the_metadata_it_recorded(tmp_path: Path):
    client = _client(_transport())
    source = MailFolderSource(_folder(client))
    item = source.list_items()[0]
    target = MailExportTarget(tmp_path)

    target.write(item, source.read(item))

    assert target.read_metadata(item)["subject"] == item.metadata["subject"]
    assert target.checksum(item) == source.checksum(item)


def test_export_job_round_trip(tmp_path: Path):
    client = _client(_transport())
    job = MigrationJob(MailFolderSource(_folder(client), MailExportOptions()), MailExportTarget(tmp_path))

    job.plan()
    stats = job.run()
    report = job.verify()

    assert stats.success == 4  # noqa: PLR2004 - three messages plus the archive one
    assert report.ok
    assert len(list(tmp_path.rglob("*.eml"))) == 4  # noqa: PLR2004
    assert (tmp_path / MANIFEST_NAME).exists()


def test_resumed_export_skips_what_is_already_on_disk(tmp_path: Path):
    client = _client(_transport())
    source = MailFolderSource(_folder(client))
    for item in source.list_items():
        MailExportTarget(tmp_path).write(item, source.read(item))

    job = MigrationJob(MailFolderSource(_folder(client)), MailExportTarget(tmp_path))
    job.plan()
    stats = job.run()

    assert stats.success == 0
    assert stats.skipped == 4  # noqa: PLR2004


def test_preserve_timestamps_stamps_the_file(tmp_path: Path):
    client = _client(_transport())
    source = MailFolderSource(_folder(client))
    item = source.list_items()[0]
    target = MailExportTarget(tmp_path)
    target.write(item, source.read(item))

    target.apply_timestamps(item)

    stamped = datetime.fromtimestamp((tmp_path / item.dest_path).stat().st_mtime, timezone.utc)
    assert stamped == datetime(2024, 3, 1, 9, 16, tzinfo=timezone.utc)
