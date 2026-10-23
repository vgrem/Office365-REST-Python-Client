"""Async large-file upload tests (offline).

Covers the reusable chunk loop on :class:`UploadSessionRequest` and the
awaitable :meth:`DriveItem.resumable_upload_async` twin: chunks are read off the
event loop and PUT in order through the configured async transport.
"""

from __future__ import annotations

import asyncio
import threading
from unittest import mock

from office365.graph_client import GraphClient
from office365.onedrive.driveitems.driveItem import DriveItem
from office365.runtime.client_request_exception import ClientRequestException
from office365.runtime.odata.v4.upload_session_request import UploadSessionRequest
from tests._scripted_transport import AsyncScriptedTransport, RoutingTransport

_UPLOAD_URL = "https://upload.contoso.example/session"


class _RecordingAsyncTransport(AsyncScriptedTransport):
    """Native-async transport that records every request it receives."""

    def __init__(self, payloads: list) -> None:
        super().__init__(payloads)
        self.requests: list = []

    async def execute_async(self, request):
        self.requests.append(request)
        return await super().execute_async(request)


class _ThreadRecordingFile:
    """File wrapper recording the thread each ``read`` runs on."""

    def __init__(self, handle) -> None:
        self._handle = handle
        self.reads: list[int] = []

    def read(self, size):
        self.reads.append(threading.get_ident())
        return self._handle.read(size)

    def fileno(self):
        return self._handle.fileno()

    def tell(self):
        return self._handle.tell()

    def seek(self, offset, whence=0):
        return self._handle.seek(offset, whence)

    def close(self):
        self._handle.close()


def test_upload_session_request_async_uploads_ranges(tmp_path) -> None:
    source = tmp_path / "payload.bin"
    source.write_bytes(b"abcdefghij")  # 10 bytes
    loop_thread = threading.get_ident()
    file_object = _ThreadRecordingFile(source.open("rb"))
    transport = _RecordingAsyncTransport([{"d": {}}] * 3)
    request = UploadSessionRequest(file_object, chunk_size=4)
    request.with_async_transport(transport)
    query = mock.Mock(upload_session_url=_UPLOAD_URL)

    asyncio.run(request.execute_query_async(query))

    assert transport.calls == 3  # noqa: PLR2004
    assert [r.headers["Content-Range"] for r in transport.requests] == [
        "bytes 0-3/10",
        "bytes 4-7/10",
        "bytes 8-9/10",
    ]
    assert [r.headers["Content-Length"] for r in transport.requests] == ["4", "4", "2"]
    assert file_object.reads and all(thread != loop_thread for thread in file_object.reads)


def test_drive_item_resumable_upload_async_end_to_end(tmp_path) -> None:
    source = tmp_path / "hello.bin"
    source.write_bytes(b"x" * 10)
    ctx = GraphClient()
    transport = RoutingTransport(
        [
            ("createUploadSession", {"uploadUrl": _UPLOAD_URL}),
            (_UPLOAD_URL, {"d": {}}),
        ]
    )
    ctx.pending_request().beforeExecute.clear()
    ctx.pending_request().transport = transport
    seen: list = []

    uploaded = asyncio.run(ctx.me.drive.root.resumable_upload_async(str(source), chunk_size=4, progress=seen.append))

    assert isinstance(uploaded, DriveItem)
    assert len([url for url in transport.calls if "createUploadSession" in url]) == 1
    assert len([url for url in transport.calls if url.startswith(_UPLOAD_URL)]) == 3  # noqa: PLR2004
    assert [p.done for p in seen] == [4, 8, 10]
    assert seen[-1].total == 10  # noqa: PLR2004
    assert seen[-1].stage == "uploading"


def test_drive_item_resumable_upload_async_dispatches_to_on_error(tmp_path) -> None:
    source = tmp_path / "hello.bin"
    source.write_bytes(b"x" * 4)
    ctx = GraphClient()
    transport = RoutingTransport(
        [
            ("createUploadSession", {"uploadUrl": _UPLOAD_URL}),
            (_UPLOAD_URL, {"status": 500, "body": {"error": {"message": "boom"}}}),
        ]
    )
    ctx.pending_request().beforeExecute.clear()
    ctx.pending_request().transport = transport
    handled: list = []
    ctx.pending_request().on_error(handled.append)

    uploaded = asyncio.run(ctx.me.drive.root.resumable_upload_async(str(source), chunk_size=4))

    assert isinstance(uploaded, DriveItem)
    assert len(handled) == 1
    assert isinstance(handled[0], ClientRequestException)
