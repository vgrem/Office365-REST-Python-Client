"""Async large-file upload tests for SharePoint (offline).

Covers ``FileCollection.create_upload_session_async``: the placeholder file is
created, then each chunk is read off the event loop and PUT through the async
transport, in order, with ``chunk_uploaded``/``progress`` parity to the
synchronous twin.
"""

from __future__ import annotations

import asyncio

import pytest
from office365.runtime.client_request_exception import ClientRequestException
from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.files.collection import FileCollection
from tests._scripted_transport import RoutingTransport

_SITE_URL = "https://contoso.sharepoint.com/sites/dev"
_ROOT = "/sites/dev/Shared Documents"


def _context(routes: list[tuple[str, object]]) -> tuple[ClientContext, RoutingTransport]:
    ctx = ClientContext(_SITE_URL)
    ctx.pending_request().beforeExecute.clear()
    transport = RoutingTransport(routes)
    ctx.pending_request().transport = transport
    return ctx, transport


def _collection(ctx: ClientContext) -> FileCollection:
    folder = ctx.web.get_folder_by_server_relative_url(_ROOT)
    folder.set_property("ServerRelativeUrl", _ROOT)
    return folder.files


_ROUTES = [
    ("/add", {"d": {"__metadata": {"type": "SP.File"}, "Name": "big.bin", "Length": "10"}}),
    ("startUpload", {"d": {"startUpload": 4}}),
    ("continueUpload", {"d": {"continueUpload": 8}}),
    ("finishUpload", {"d": {"Name": "big.bin", "Length": "10"}}),
]


def test_create_upload_session_async_uploads_chunks(tmp_path) -> None:
    source = tmp_path / "big.bin"
    source.write_bytes(b"abcdefghij")  # 10 bytes
    ctx, transport = _context(list(_ROUTES))
    col = _collection(ctx)
    uploaded: list[int] = []
    seen: list = []

    uploaded_file = asyncio.run(
        col.create_upload_session_async(str(source), chunk_size=4, chunk_uploaded=uploaded.append, progress=seen.append)
    )

    assert uploaded_file is not None
    assert sum(1 for url in transport.calls if "/add(" in url) == 1
    assert sum(1 for url in transport.calls if "startUpload" in url) == 1
    assert sum(1 for url in transport.calls if "continueUpload" in url) == 1
    assert sum(1 for url in transport.calls if "finishUpload" in url) == 1
    chunk_requests = [r for r in transport.requests if "Upload" in r.url]
    assert [len(r.data) for r in chunk_requests] == [4, 4, 2]
    # Offset semantics match the synchronous twin: the offset of the chunk about
    # to be sent, then the full size once everything is committed.
    assert uploaded == [0, 4, 8, 10]
    assert [p.done for p in seen] == [0, 4, 8, 10]
    assert seen[-1].total == 10  # noqa: PLR2004
    assert seen[-1].stage == "uploading"


def test_create_upload_session_async_propagates_failure(tmp_path) -> None:
    source = tmp_path / "big.bin"
    source.write_bytes(b"abcdefghij")
    ctx, _ = _context(
        [
            ("/add", {"d": {"__metadata": {"type": "SP.File"}, "Name": "big.bin"}}),
            ("startUpload", {"d": {"startUpload": 4}}),
            ("continueUpload", {"d": {"continueUpload": 8}}),
            ("finishUpload", {"status": 500, "body": {"error": {"message": "boom"}}}),
        ]
    )
    col = _collection(ctx)

    with pytest.raises(ClientRequestException):
        asyncio.run(col.create_upload_session_async(str(source), chunk_size=4))
