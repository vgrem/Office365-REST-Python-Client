"""Merged unit tests (consolidated; see git history for originals)."""

from __future__ import annotations

import json
import unittest
from datetime import datetime, timezone
from pathlib import Path

from office365.graph_client import GraphClient
from office365.migration import MigrationJob
from office365.migration.teams import TeamsArchiveSource, TeamsArchiveTarget, TeamsExportOptions
from office365.runtime.transport.base import BaseTransport
from requests import Response
from tests._scripted_transport import ScriptedTransport

_TEAM = {"id": "t1", "displayName": "Alpha", "visibility": "public", "mailNickname": "alpha"}
_CHANNELS = {"value": [{"id": "c1", "displayName": "General", "membershipType": "standard"}]}
_MESSAGES = {"value": [{"id": "msg1", "body": {"content": "hi"}, "createdDateTime": "2024-01-01T10:00:00Z"}]}
_REPLIES = {"value": []}


class _Transport(BaseTransport):
    def __init__(self, payloads: list[tuple[str, object]]):
        super().__init__()
        self._payloads = payloads

    def execute(self, request):
        kind, payload = self._payloads.pop(0)
        resp = Response()
        resp.status_code = 200
        resp.url = request.url
        if kind == "raw":
            resp.headers["Content-Type"] = "application/octet-stream"
            resp._content = payload  # type: ignore[assignment]
        else:
            resp.headers["Content-Type"] = "application/json"
            resp._content = json.dumps(payload).encode()
        return resp


def _client(transport) -> GraphClient:
    client = GraphClient()
    client.pending_request().beforeExecute.clear()
    client.pending_request().transport = transport
    return client


def _options() -> TeamsExportOptions:
    return TeamsExportOptions(include_members=False, include_tabs=False, include_apps=False)


def test_archive_job_round_trip(tmp_path: Path):
    payloads = [
        ("json", _CHANNELS),  # source.list_items -> channels
        ("json", _MESSAGES),  # source.list_items -> messages
        ("json", _REPLIES),  # replies
        ("json", _TEAM),  # run: structure read
        ("json", _TEAM),  # verify: structure checksum
    ]
    client = _client(_Transport(payloads))
    job = MigrationJob(
        TeamsArchiveSource(client, ["t1"], _options()),
        TeamsArchiveTarget(tmp_path),
    )

    job.plan()
    stats = job.run()
    report = job.verify()

    assert stats.success == 2  # noqa: PLR2004
    assert report.ok
    team = json.loads((tmp_path / "t1" / "team.json").read_text())
    assert team["display_name"] == "Alpha"
    lines = (tmp_path / "t1" / "messages.ndjson").read_text().strip().splitlines()
    assert json.loads(lines[0])["channel_id"] == "c1"


_MESSAGE = {
    "id": "m1",
    "replyToId": "root1",
    "messageType": "message",
    "etag": "e1",
    "createdDateTime": "2024-01-01T10:00:00Z",
    "lastModifiedDateTime": "2024-01-01T10:05:00Z",
    "from": {"user": {"id": "u1", "displayName": "Alice"}},
    "body": {"contentType": "html", "content": "hello"},
    "mentions": [{"id": 0, "mentionText": "@Bob"}],
    "reactions": [{"reactionType": "like"}],
    "hostedContents": [{"id": "hc1", "contentType": "image/png"}],
}


class teamsmessages__CaptureTransport(BaseTransport):
    def __init__(self, content: bytes = b"", content_type: str = "application/octet-stream"):
        super().__init__()
        self.urls: list[str] = []
        self._content = content
        self._content_type = content_type

    def execute(self, request):
        self.urls.append(request.url)
        resp = Response()
        resp.status_code = 200
        resp.url = request.url
        resp.headers["Content-Type"] = self._content_type
        resp._content = self._content
        return resp


def test_team_get_all_messages_parses_rich_fields():
    client = _client(ScriptedTransport([{"value": [_MESSAGE]}]))
    messages = client.teams.get_all_messages().execute_query()

    assert len(messages) == 1
    message = messages[0]
    assert message.id == "m1"
    assert message.reply_to_id == "root1"
    assert message.message_type == "message"
    assert message.etag == "e1"
    assert message.from_.user.displayName == "Alice"
    assert len(message.mentions) == 1
    assert len(message.reactions) == 1
    assert message.hosted_contents[0].id == "hc1"


def test_chat_get_all_messages_filter_in_url():
    transport = teamsmessages__CaptureTransport(
        content=json.dumps({"value": []}).encode(), content_type="application/json"
    )
    client = _client(transport)

    client.chats.get_all_messages().filter("createdDateTime gt 2024-01-01T00:00:00Z").execute_query()

    assert any("getAllMessages" in url for url in transport.urls)
    assert any("$filter" in url for url in transport.urls)


def test_visible_history_start_datetime_is_set():
    client = _client(ScriptedTransport([]))
    team = client.teams["t1"]
    start = datetime(2024, 1, 1, tzinfo=timezone.utc)

    member = team.members.add(user="u1", roles=["member"], visible_history_start_datetime=start)

    assert member.get_property("visibleHistoryStartDateTime") == start


def test_download_hosted_contents_deferred(tmp_path):
    client = _client(
        _Transport(
            [
                ("json", {"value": [_MESSAGE]}),
                ("raw", b"\x89PNG"),
            ]
        )
    )
    channel = client.teams["t1"].channels["c1"]

    channel.messages.get_all().download_hosted_contents(tmp_path).execute_query()

    assert (tmp_path / "m1_hc1.png").read_bytes() == b"\x89PNG"


def _item(item_id: str, name: str) -> dict:
    return {"id": item_id, "name": name, "folder": {}, "@odata.type": "#microsoft.graph.driveItem"}


class driveitemensurefolder__CaptureTransport(BaseTransport):
    def __init__(self, responses: list[tuple[int, dict]]):
        super().__init__()
        self._responses = responses
        self.urls: list[str] = []

    def execute(self, request):
        status, body = self._responses.pop(0)
        self.urls.append(request.url)
        resp = Response()
        resp.status_code = status
        resp.url = request.url
        resp.headers["Content-Type"] = "application/json"
        resp._content = json.dumps(body).encode()
        return resp


class TestDriveItemEnsureFolder(unittest.TestCase):
    def _client(self, responses=None) -> tuple[GraphClient, driveitemensurefolder__CaptureTransport]:
        client = GraphClient()
        if responses is None:
            responses = [
                (200, {"value": []}),  # GET root children (a) — miss
                (201, _item("a1", "a")),  # POST a
                (200, {"value": []}),  # GET /items/a1/children (b) — miss
                (201, _item("b2", "b")),  # POST b
                (200, {"value": []}),  # GET /items/b2/children (c) — miss
                (201, _item("c3", "c")),  # POST c
            ]
        transport = driveitemensurefolder__CaptureTransport(responses)
        client.pending_request().beforeExecute.clear()
        client.pending_request().transport = transport
        return client, transport

    def test_creates_missing_nested_folders(self):
        client, transport = self._client()

        target = client.me.drive.root.ensure_folder("a/b/c")
        client.execute_query()

        self.assertEqual(target.get_property("id"), "c3")
        self.assertEqual(target.get_property("name"), "c")
        self.assertEqual(len(transport.urls), 6)  # 3 children lookups + 3 creates
        self.assertIn("/me/drive/root/children", transport.urls[0])
        self.assertIn("/me/drive/items/a1/children", transport.urls[2])
        self.assertIn("/me/drive/items/b2/children", transport.urls[4])
        # Reads must never use path-addressing on an id (``/items/{id}:/...``).
        paths = [url.split("graph.microsoft.com", 1)[-1] for url in transport.urls]
        self.assertFalse(any(":/" in path for path in paths))


def _file_item(item_id: str, name: str) -> dict:
    return {"id": item_id, "name": name, "file": {}, "@odata.type": "#microsoft.graph.driveItem"}


class driveitemensurefile__CaptureTransport(BaseTransport):
    def __init__(self, responses: list[tuple[int, dict]]):
        super().__init__()
        self._responses = responses
        self.calls: list[tuple[str, str, object]] = []

    def execute(self, request):
        status, body = self._responses.pop(0)
        self.calls.append((str(request.method), request.url, request.data))
        resp = Response()
        resp.status_code = status
        resp.url = request.url
        resp.headers["Content-Type"] = "application/json"
        resp._content = json.dumps(body).encode()
        return resp


class TestDriveItemEnsureFile(unittest.TestCase):
    def _client(self, responses: list[tuple[int, dict]]):
        client = GraphClient()
        transport = driveitemensurefile__CaptureTransport(responses)
        client.pending_request().beforeExecute.clear()
        client.pending_request().transport = transport
        return client, transport

    def test_reuses_existing_file(self):
        client, transport = self._client([(200, {"value": [_file_item("f1", "f.txt")]})])

        target = client.me.drive.root.ensure_file("f.txt", b"hi")
        client.execute_query()

        self.assertEqual(len(transport.calls), 1)
        method, url, _ = transport.calls[0]
        self.assertEqual(method, "GET")
        self.assertIn("children", url)
        self.assertIn("f.txt", url)
        self.assertEqual(target.get_property("id"), "f1")

    def test_uploads_into_nested_folder(self):
        client, transport = self._client(
            [
                (200, {"value": []}),  # GET /root/children (a) — miss
                (201, _item("a1", "a")),  # POST a
                (200, {"value": []}),  # GET /items/a1/children (b) — miss
                (201, _item("b2", "b")),  # POST b
                (200, {"value": []}),  # GET /items/b2/children (f.txt) — miss
                (201, _file_item("f4", "f.txt")),  # PUT /items/b2:/f.txt:/content
            ]
        )

        target = client.me.drive.root.ensure_file("a/b/f.txt", b"hi")
        client.execute_query()

        method, url, data = transport.calls[-1]
        self.assertEqual(method, "PUT")
        self.assertTrue(url.endswith("/items/b2:/f.txt:/content"))
        self.assertEqual(data, b"hi")
        self.assertEqual(target.get_property("id"), "f4")
