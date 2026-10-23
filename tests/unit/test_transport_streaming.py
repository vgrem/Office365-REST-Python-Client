"""Offline tests for the streaming transport contract and async downloads.

Covers the default :meth:`BaseTransport.stream` / :meth:`BaseTransport.stream_async`
(one chunk per worker wait, response closed on early exit), the ``on_headers``
hook used to read ``Content-Length`` for progress, and
:meth:`File.download_session_async` — the awaitable twin of
``download_session`` that streams a large file without buffering it or blocking
the event loop.
"""

from __future__ import annotations

import asyncio
import io
import threading
from typing import Any

import pytest
from office365.graph_client import GraphClient
from office365.runtime.client_request_exception import ClientRequestException
from office365.runtime.http.request_options import RequestOptions
from office365.runtime.transport.base import BaseTransport
from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.files.file import File
from tests._scripted_transport import ScriptedTransport, build_response

_URL = "https://contoso.sharepoint.com/_api/web/GetFileByServerRelativeUrl('a.bin')/$value"
_SITE_URL = "https://contoso.sharepoint.com/sites/dev"
_FILE_URL = "/sites/dev/Shared Documents/a.bin"
_BODY = b"0123456789" * 100


class _BodyTransport(BaseTransport):
    """Materialised, scripted body served through the default streaming helpers."""

    def __init__(self, body: bytes, *, status: int = 200, headers: dict[str, str] | None = None) -> None:
        self._body = body
        self._status = status
        self._headers = headers or {}
        self.threads: list[int] = []

    def execute(self, request: RequestOptions):
        self.threads.append(threading.get_ident())
        response = build_response(request, self._body)
        response.status_code = self._status
        response.headers.update(self._headers)
        return response


def test_stream_async_offloads_and_concatenates() -> None:
    loop_thread = threading.get_ident()
    transport = _BodyTransport(b"0123456789")

    async def _run() -> bytes:
        return b"".join([chunk async for chunk in transport.stream_async(RequestOptions(url=_URL), chunk_size=4)])

    assert asyncio.run(_run()) == b"0123456789"
    assert transport.threads and transport.threads[0] != loop_thread


def test_stream_flows_through_throttled_transport() -> None:
    """The inherited ``stream`` still goes through the paced ``execute``."""
    from office365.runtime.http.throttling import RateLimiter
    from office365.runtime.transport.throttled_transport import ThrottledTransport

    inner = _BodyTransport(b"paced-body", headers={"X-SharePointHealthScore": "100"})
    limiter = RateLimiter(clock=lambda: 0.0)
    transport = ThrottledTransport(inner, limiter)

    chunks = list(transport.stream(RequestOptions(url=_URL), chunk_size=4))

    assert b"".join(chunks) == b"paced-body"
    # The response was fed back into the shared limiter (health score 100 -> 1s gate).
    assert limiter.snapshot().next_available_at > 0.0


def test_stream_async_flows_through_throttled_transport() -> None:
    from office365.runtime.http.throttling import RateLimiter
    from office365.runtime.transport.throttled_transport import ThrottledTransport

    inner = _BodyTransport(b"paced-body")
    transport = ThrottledTransport(inner, RateLimiter())

    async def _run() -> bytes:
        return b"".join([chunk async for chunk in transport.stream_async(RequestOptions(url=_URL), chunk_size=4)])

    assert asyncio.run(_run()) == b"paced-body"


class _RecordingStreamingTransport(ScriptedTransport):
    def __init__(self, payloads: list) -> None:
        super().__init__(payloads)
        self.threads: list[int] = []

    def execute(self, request):
        self.threads.append(threading.get_ident())
        return super().execute(request)


class _NativeAsyncStreamTransport(BaseTransport):
    """Native-async transport that only implements ``stream_async``."""

    def __init__(self, body: bytes) -> None:
        self._body = body
        self.calls = 0
        self.threads: list[int] = []

    def execute(self, request):
        raise AssertionError("the native async transport must not use the sync path")

    async def stream_async(self, request, chunk_size=8192, on_headers=None):  # type: ignore[override]
        self.calls += 1
        self.threads.append(threading.get_ident())
        if on_headers is not None:
            on_headers({"Content-Length": str(len(self._body))})
        for index in range(0, len(self._body), chunk_size):
            yield self._body[index : index + chunk_size]


def _file_context(body: bytes, *, transport: BaseTransport | None = None):
    ctx = ClientContext(_SITE_URL)
    ctx.pending_request().beforeExecute.clear()
    transport = transport or ScriptedTransport([body])
    ctx.pending_request().transport = transport
    file = File(ctx)
    file.set_property("Id", "1")
    file.set_property("ServerRelativePath", _FILE_URL)
    file.set_property("ServerRelativeUrl", _FILE_URL)
    return ctx, file, transport


def test_download_session_async_writes_file_off_loop() -> None:
    loop_thread = threading.get_ident()
    transport = _RecordingStreamingTransport([_BODY])
    _, file, _ = _file_context(_BODY, transport=transport)
    stream = io.BytesIO()

    result = asyncio.run(file.download_session_async(stream, chunk_size=1024))

    assert result is file
    assert stream.getvalue() == _BODY
    assert transport.calls == 1
    assert transport.threads[0] != loop_thread


def test_download_session_async_reports_chunks_and_progress() -> None:
    body = b"a" * 10
    _, file, _ = _file_context(body)
    stream = io.BytesIO()
    chunks: list[int] = []
    progress: list[Any] = []

    asyncio.run(
        file.download_session_async(stream, chunk_downloaded=chunks.append, chunk_size=4, progress=progress.append)
    )

    assert stream.getvalue() == body
    assert chunks == [4, 8, 10]
    assert [p.done for p in progress] == [4, 8, 10]
    assert progress[-1].total == 10  # noqa: PLR2004
    assert progress[-1].stage == "downloading"


def test_download_session_async_dispatches_to_on_error() -> None:
    ctx = ClientContext(_SITE_URL)
    ctx.pending_request().beforeExecute.clear()
    ctx.pending_request().transport = ScriptedTransport([{"status": 404, "body": {"error": {"message": "missing"}}}])
    file = File(ctx)
    file.set_property("Id", "1")
    file.set_property("ServerRelativePath", _FILE_URL)
    file.set_property("ServerRelativeUrl", _FILE_URL)
    handled: list[ClientRequestException] = []
    ctx.pending_request().on_error(handled.append)

    result = asyncio.run(file.download_session_async(io.BytesIO()))

    assert result is file
    assert len(handled) == 1


def _drive_item_context(body: bytes, *, transport: BaseTransport | None = None):
    ctx = GraphClient()
    ctx.pending_request().beforeExecute.clear()
    transport = transport or ScriptedTransport([body])
    ctx.pending_request().transport = transport
    return ctx, ctx.me.drive.root, transport


def test_drive_item_download_session_async_reports_chunks_and_progress() -> None:
    body = b"a" * 10
    _, item, _ = _drive_item_context(body)
    stream = io.BytesIO()
    chunks: list[int] = []
    progress: list[Any] = []

    asyncio.run(
        item.download_session_async(stream, chunk_downloaded=chunks.append, chunk_size=4, progress=progress.append)
    )

    assert stream.getvalue() == body
    assert chunks == [4, 8, 10]
    assert [p.done for p in progress] == [4, 8, 10]
    assert progress[-1].total == 10  # noqa: PLR2004
    assert progress[-1].stage == "downloading"


def test_drive_item_download_session_async_dispatches_to_on_error() -> None:
    ctx = GraphClient()
    ctx.pending_request().beforeExecute.clear()
    ctx.pending_request().transport = ScriptedTransport([{"status": 404, "body": {"error": {"message": "missing"}}}])
    handled: list[ClientRequestException] = []
    ctx.pending_request().on_error(handled.append)
    item = ctx.me.drive.root

    result = asyncio.run(item.download_session_async(io.BytesIO()))

    assert result is item
    assert len(handled) == 1


# -- async content streams (get_content_stream_async) ------------------------


def test_file_get_content_stream_async_yields_chunks() -> None:
    _, file, _ = _file_context(_BODY)

    async def _run() -> list[bytes]:
        return [chunk async for chunk in file.get_content_stream_async(chunk_size=256)]

    chunks = asyncio.run(_run())

    assert b"".join(chunks) == _BODY
    assert [len(c) for c in chunks] == [256, 256, 256, 232]


def test_file_get_content_stream_async_invokes_on_headers() -> None:
    _, file, _ = _file_context(b"abc")
    seen: list[Any] = []

    async def _run() -> bytes:
        return b"".join([chunk async for chunk in file.get_content_stream_async(on_headers=seen.append)])

    assert asyncio.run(_run()) == b"abc"
    assert seen[0]["Content-Length"] == "3"


def test_file_get_content_stream_async_raises_client_request_exception() -> None:
    ctx = ClientContext(_SITE_URL)
    ctx.pending_request().beforeExecute.clear()
    ctx.pending_request().transport = ScriptedTransport([{"status": 404, "body": {"error": {"message": "missing"}}}])
    file = File(ctx)
    file.set_property("Id", "1")
    file.set_property("ServerRelativePath", _FILE_URL)
    file.set_property("ServerRelativeUrl", _FILE_URL)

    async def _run() -> list[bytes]:
        return [chunk async for chunk in file.get_content_stream_async()]

    with pytest.raises(ClientRequestException):
        asyncio.run(_run())


def test_drive_item_get_content_stream_async_uses_native_async_stream() -> None:
    transport = _NativeAsyncStreamTransport(_BODY)
    _, item, _ = _drive_item_context(_BODY, transport=transport)

    async def _run() -> bytes:
        return b"".join([chunk async for chunk in item.get_content_stream_async(chunk_size=256)])

    assert asyncio.run(_run()) == _BODY
    assert transport.calls == 1
    assert transport.threads == [threading.get_ident()]


def test_get_content_stream_async_closes_on_early_exit() -> None:
    closed: list[bool] = []

    class _Cancellable(BaseTransport):
        def execute(self, request: RequestOptions):
            return build_response(request, b"content")

        async def stream_async(self, request, chunk_size=8192, on_headers=None):  # type: ignore[override]
            try:
                yield b"first"
                yield b"second"
            finally:
                closed.append(True)

    ctx = GraphClient()
    ctx.pending_request().beforeExecute.clear()
    ctx.pending_request().transport = _Cancellable()

    async def _run() -> bytes:
        stream = ctx.me.drive.root.get_content_stream_async()
        first = await stream.__anext__()
        await stream.aclose()
        return first

    assert asyncio.run(_run()) == b"first"
    assert closed == [True]


# -- context lifecycle (close / aclose) --------------------------------------


class _ClosableTransport(BaseTransport):
    """Records explicit close calls on both the sync and async paths."""

    def __init__(self) -> None:
        self.closed = 0
        self.aclosed = 0

    def execute(self, request: RequestOptions):
        return build_response(request, b"")

    def close(self) -> None:
        self.closed += 1

    async def aclose(self) -> None:
        self.aclosed += 1


def test_context_close_releases_transport() -> None:
    ctx = ClientContext(_SITE_URL)
    transport = _ClosableTransport()
    ctx.pending_request().transport = transport

    ctx.close()

    assert transport.closed == 1


def test_async_with_closes_transport() -> None:
    ctx = ClientContext(_SITE_URL)
    transport = _ClosableTransport()
    ctx.pending_request().transport = transport

    async def _run() -> None:
        async with ctx as entered:
            assert entered is ctx

    asyncio.run(_run())

    assert transport.aclosed == 1
