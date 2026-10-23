"""Mail import: an EML tree as the source, a mailbox as the target (offline).

The transport scripts Graph the way Exchange answers a MIME import: a POST that
returns the created message, a `$value` read that hands back the message
*re-serialized* (headers reflowed, an HTML `<meta>` prefix added), a folder listing
used to recognise what was already delivered, and a PATCH for the envelope flags.
"""

from __future__ import annotations

import base64
import email
import hashlib
import json
from email.message import EmailMessage
from email.policy import SMTP
from pathlib import Path
from typing import Any

from office365.graph_client import GraphClient
from office365.migration import MigrationJob
from office365.migration.outlook import EmlTreeSource, MailboxTarget, mime_digest
from tests._scripted_transport import MethodRoutingTransport

_INBOX_ID = "inbox"
_ARCHIVE_ID = "f-1"
_SUBJECT = "Quarterly report \u2014 Q1"
_ONE_MB = 1024 * 1024


def _eml(
    subject: str = _SUBJECT,
    body: str = "body\r\n",
    html: bool = True,
    attachment: bytes | None = None,
) -> bytes:
    message = EmailMessage(policy=SMTP)
    message["From"] = "Alice <alice@contoso.com>"
    message["To"] = "Bob <bob@contoso.com>"
    message["Subject"] = subject
    message["Date"] = "Mon, 04 Mar 2024 09:15:00 +0000"
    message["Message-ID"] = f"<{hashlib.sha1(subject.encode()).hexdigest()[:12]}@contoso.com>"
    message.set_content(body)
    if html:
        message.add_alternative(f"<p>{body.strip()}</p>", subtype="html")
    if attachment is not None:
        message.add_attachment(attachment, maintype="application", subtype="octet-stream", filename="blob.bin")
    return message.as_bytes()


def _parse(data: bytes):
    return email.message_from_bytes(data, policy=SMTP)


def _reserialize(data: bytes) -> bytes:
    """What Exchange does to an imported message: reflow headers, tag the HTML body."""
    message = _parse(data)
    for part in message.walk():
        if part.get_content_type() == "text/html":
            tag = b'<meta http-equiv="Content-Type" content="text/html; charset=utf-8">'
            part.set_payload(tag + part.get_payload(decode=True), charset="utf-8")
    return message.as_bytes()


def _write_tree(root: Path, files: dict[str, bytes], display_paths: dict[str, str] | None = None) -> Path:
    """Write an exported tree: an ``.eml`` plus the sidecar the export records."""
    for relative, payload in files.items():
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(payload)
        parsed = _parse(payload)
        envelope: dict[str, Any] = {
            "internet_message_id": parsed["Message-ID"],
            "subject": parsed["Subject"],
            "received": "2024-03-04T09:15:00+00:00",
            "categories": ["Finance"],
            "is_read": False,
            "importance": "normal",
        }
        display = (display_paths or {}).get(relative)
        if display:
            envelope["folder_display_path"] = display
        path.with_suffix(".json").write_text(json.dumps(envelope), encoding="utf-8")
    return root


class _Mailbox:
    """A fake Exchange mailbox: folders, MIME import, folder listings and PATCHes."""

    def __init__(self, rewrite=_reserialize, create_extra: dict[str, Any] | None = None) -> None:
        self.rewrite = rewrite
        #: Extra properties the create response reports, as Exchange's does (it echoes
        #: the attachments a MIME import just produced).
        self.create_extra = create_extra or {}
        self.messages: dict[str, bytes] = {}  # graph id -> the bytes a $value read returns
        self.owners: dict[str, str] = {}  # graph id -> folder id
        self.posted: list[tuple[str, bytes, str]] = []  # (folder id, raw MIME, Content-Type)
        self.patched: list[tuple[str, dict[str, Any]]] = []
        self.folders: list[tuple[str, str]] = []  # (parent folder id or "", display name)

    def routes(self):
        # Deeper routes first: the table matches the first URL substring that fits.
        return [
            (None, "/$value", self._mime),
            ("PATCH", "/messages/", self._patch),
            ("GET", "/messages?", self._listing),
            ("POST", "/messages", self._import),
            (None, "/childFolders", self._folder),
            (None, f"/mailFolders/{_INBOX_ID}", {"id": _INBOX_ID, "displayName": "Inbox", "childFolderCount": 1}),
        ]

    def _folder_of(self, url: str) -> str:
        """The folder a URL addresses — the deepest ``childFolders`` id, else the root."""
        base = url.split("?", maxsplit=1)[0].removesuffix("/childFolders")
        if "/childFolders/" in base:
            return base.rsplit("/childFolders/", 1)[1].split("/")[0]
        return _INBOX_ID

    def _mime(self, request):
        return self.messages[request.url.split("/messages/")[1].split("/")[0]]

    def _patch(self, request):
        message_id = request.url.split("/messages/")[1].split("/")[0]
        self.patched.append((message_id, request.data))
        return {"id": message_id}

    def _listing(self, request):
        folder_id = self._folder_of(request.url)
        return {
            "value": [
                {"id": key, "internetMessageId": _parse(data)["Message-ID"]}
                for key, data in self.messages.items()
                if self.owners[key] == folder_id
            ]
        }

    def _import(self, request):
        folder_id = self._folder_of(request.url)
        raw = base64.b64decode(request.data)
        self.posted.append((folder_id, raw, request.headers.get("Content-Type")))
        message_id = f"m{len(self.messages) + 1}"
        self.messages[message_id] = self.rewrite(raw)
        self.owners[message_id] = folder_id
        parsed = _parse(raw)
        return {
            "id": message_id,
            "internetMessageId": parsed["Message-ID"],
            "subject": parsed["Subject"],
            "isDraft": True,
            "isRead": True,
            **self.create_extra,
        }

    def _folder(self, request):
        """``ensure()`` creates first and falls back to a filtered read on a duplicate."""
        parent = self._folder_of(request.url)
        if _verb(request) == "POST":
            name = request.data["displayName"]
            self.folders.append((parent, name))
            return {"id": f"f-{len(self.folders)}", "displayName": name}
        return {
            "value": [
                {"id": f"f-{index + 1}", "displayName": name}
                for index, (owner, name) in enumerate(self.folders)
                if owner == parent
            ]
        }


def _verb(request) -> str:
    return str(getattr(request.method, "value", request.method)).upper()


def _client(mailbox: _Mailbox) -> GraphClient:
    client = GraphClient()
    client.pending_request().beforeExecute.clear()
    client.pending_request().transport = MethodRoutingTransport(mailbox.routes())
    return client


def _inbox(client: GraphClient):
    return client.me.mail_folders[_INBOX_ID].get().execute_query()


def _tree(tmp_path: Path, files: dict[str, bytes] | None = None, display_paths=None) -> Path:
    return _write_tree(tmp_path / "export", files or {"Inbox/m1.eml": _eml()}, display_paths)


def test_source_reads_the_exported_tree(tmp_path: Path):
    root = _tree(tmp_path, {"Inbox/m1.eml": _eml(), "Inbox/Archive/m2.eml": _eml("Old thread")})

    items = EmlTreeSource(root).list_items()

    assert [item.dest_path for item in items] == ["Inbox/Archive/m2.eml", "Inbox/m1.eml"]
    assert all(item.item_type == "file" for item in items)
    assert items[0].metadata["categories"] == ["Finance"]
    assert items[0].metadata["is_read"] is False
    assert items[0].created == "2024-03-04T09:15:00+00:00"


def test_source_digests_what_the_message_says(tmp_path: Path):
    payload = _eml(attachment=b"\x00\x01blob")
    root = _tree(tmp_path, {"Inbox/m1.eml": payload})
    source = EmlTreeSource(root)
    item = source.list_items()[0]

    assert source.read(item) == payload
    assert source.checksum(item) == mime_digest(payload)


def test_import_delivers_base64_mime_and_creates_the_folder_chain(tmp_path: Path):
    mailbox = _Mailbox()
    client = _client(mailbox)
    payload = _eml()
    job = MigrationJob(EmlTreeSource(_tree(tmp_path, {"Inbox/Archive/m2.eml": payload})), MailboxTarget(_inbox(client)))

    job.plan()
    stats = job.run()

    assert stats.success == 1
    assert mailbox.folders == [(_INBOX_ID, "Archive")]
    # Graph only accepts the import as base64 text, and only with this content type.
    folder_id, raw, content_type = mailbox.posted[0]
    assert (folder_id, base64.b64encode(raw), content_type) == (_ARCHIVE_ID, base64.b64encode(payload), "text/plain")


def test_flag_replay_patches_only_the_flags_not_the_imported_message(tmp_path: Path):
    """The create response describes the whole message; the replay must not echo it back.

    Graph refuses a message PATCH carrying the attachments the import reported
    (``UnprocessableType: Cannot process input of abstract type
    'microsoft.graph.attachment'``), so the replay addresses a stub of the changed
    properties instead of the object the import returned.
    """
    mailbox = _Mailbox(
        create_extra={
            "attachments": [{"@odata.type": "#microsoft.graph.fileAttachment", "id": "att-1"}],
            "toRecipients": [{"emailAddress": {"address": "bob@contoso.com"}}],
            "body": {"contentType": "text", "content": "body"},
        }
    )
    client = _client(mailbox)
    job = MigrationJob(EmlTreeSource(_tree(tmp_path)), MailboxTarget(_inbox(client)))

    job.plan()
    job.run()

    _, properties = mailbox.patched[0]
    assert {key: properties[key] for key in ("isRead", "categories")} == {"isRead": False, "categories": ["Finance"]}
    for echoed in ("attachments", "toRecipients", "body", "subject"):
        assert echoed not in properties, echoed


def test_import_skips_a_message_it_already_delivered(tmp_path: Path):
    mailbox = _Mailbox()
    client = _client(mailbox)
    root = _tree(tmp_path)
    first = MigrationJob(EmlTreeSource(root), MailboxTarget(_inbox(client)))
    first.plan()
    first.run()

    job = MigrationJob(EmlTreeSource(root), MailboxTarget(_inbox(client)))
    job.plan()
    stats = job.run()

    assert stats.success == 0
    assert stats.skipped == 1
    assert len(mailbox.posted) == 1  # the first run's import, not a second copy


def test_import_verifies_content_across_the_rewrite(tmp_path: Path):
    mailbox = _Mailbox()
    client = _client(mailbox)
    job = MigrationJob(
        EmlTreeSource(_tree(tmp_path, {"Inbox/m1.eml": _eml(attachment=b"\x00\x01blob")})),
        MailboxTarget(_inbox(client)),
    )

    job.plan()
    job.run()
    report = job.verify()

    assert report.mismatches == []
    assert report.checked == 1


def test_import_reports_a_message_whose_body_was_altered(tmp_path: Path):
    mailbox = _Mailbox(rewrite=lambda data: _reserialize(data).replace(b"body", b"tampered"))
    client = _client(mailbox)
    job = MigrationJob(EmlTreeSource(_tree(tmp_path)), MailboxTarget(_inbox(client)))

    job.plan()
    job.run()
    report = job.verify()

    assert report.mismatches == ["content mismatch: Inbox/m1.eml"]


def test_import_refuses_a_message_over_the_mime_limit(tmp_path: Path):
    mailbox = _Mailbox()
    client = _client(mailbox)
    root = _tree(tmp_path, {"Inbox/big.eml": b"Subject: big\r\n\r\n" + b"x" * (4 * _ONE_MB + 1)})
    job = MigrationJob(EmlTreeSource(root), MailboxTarget(_inbox(client)))

    job.plan()
    stats = job.run()

    assert stats.success == 0
    assert stats.errors == 1
    assert mailbox.posted == []
