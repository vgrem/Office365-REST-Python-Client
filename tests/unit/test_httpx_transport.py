"""Tests for the optional httpx-backed transport (skipped when httpx is absent)."""

from __future__ import annotations

import asyncio
import json

import pytest
import requests
from office365.runtime.http.http_method import HttpMethod
from office365.runtime.http.request_options import RequestOptions
from office365.runtime.transport.base import NO_TIMEOUT
from office365.runtime.transport.httpx_transport import HttpxTransport
from office365.sharepoint.client_context import ClientContext

httpx = pytest.importorskip("httpx")

_URL = "https://graph.microsoft.com/v1.0/me"


def _json_handler(payload: dict):
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json=payload)

    return handler


def _transport(handler) -> HttpxTransport:
    return HttpxTransport(
        client=httpx.Client(transport=httpx.MockTransport(handler)),
        async_client=httpx.AsyncClient(transport=httpx.MockTransport(handler)),
    )


def test_execute_async_adapts_response() -> None:
    transport = _transport(_json_handler({"d": {"Title": "Contoso"}}))

    response = asyncio.run(transport.execute_async(RequestOptions(url=_URL)))

    assert response.status_code == 200  # noqa: PLR2004
    assert response.json() == {"d": {"Title": "Contoso"}}
    assert response.headers["Content-Type"].startswith("application/json")


def test_execute_async_sends_json_body() -> None:
    seen: dict[str, object] = {}

    def handler(request: httpx.Request) -> httpx.Response:
        seen["method"] = request.method
        seen["body"] = request.content
        return httpx.Response(200, json={"ok": True})

    transport = _transport(handler)
    request = RequestOptions(url=_URL, method=HttpMethod.Post, data={"Title": "x"})

    asyncio.run(transport.execute_async(request))

    assert seen["method"] == "POST"
    assert json.loads(seen["body"]) == {"Title": "x"}  # type: ignore[arg-type]


def test_default_timeout_bounds_connect_read_write_and_pool() -> None:
    transport = HttpxTransport()
    try:
        for client in (transport._client, transport._async_client):
            assert client.timeout.connect == 10.0  # noqa: PLR2004
            assert client.timeout.read == 300.0  # noqa: PLR2004
            assert client.timeout.write == 300.0  # noqa: PLR2004
            assert client.timeout.pool == 10.0  # noqa: PLR2004
    finally:
        asyncio.run(transport.aclose())


def test_no_timeout_sentinel_disables_timeout() -> None:
    transport = HttpxTransport(timeout=NO_TIMEOUT)
    try:
        assert transport._client.timeout == httpx.Timeout(None)
        assert transport._async_client.timeout == httpx.Timeout(None)
    finally:
        asyncio.run(transport.aclose())


def test_stream_async_yields_body_natively() -> None:
    body = b"0123456789" * 100

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, content=body)

    transport = _transport(handler)

    async def _run() -> bytes:
        stream = transport.stream_async(RequestOptions(url=_URL), chunk_size=16)
        return b"".join([chunk async for chunk in stream])

    assert asyncio.run(_run()) == body


def test_stream_invokes_on_headers() -> None:
    seen: list[dict] = []

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, content=b"abc")

    transport = _transport(handler)
    list(transport.stream(RequestOptions(url=_URL), on_headers=seen.append))

    assert len(seen) == 1
    assert seen[0]["content-length"] == "3"


def test_stream_async_raises_for_error_status() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(404, json={"error": {"message": "missing"}})

    transport = _transport(handler)

    async def _run() -> list[bytes]:
        return [chunk async for chunk in transport.stream_async(RequestOptions(url=_URL))]

    with pytest.raises(requests.HTTPError) as exc:
        asyncio.run(_run())

    assert exc.value.response.status_code == 404  # noqa: PLR2004
    assert exc.value.response.json() == {"error": {"message": "missing"}}


def test_execute_maps_connect_error_to_requests_connection_error() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("boom")

    transport = _transport(handler)

    with pytest.raises(requests.ConnectionError):
        transport.execute(RequestOptions(url=_URL))


def test_context_execute_query_async_uses_httpx_transport() -> None:
    ctx = ClientContext("https://contoso.sharepoint.com")
    ctx.pending_request().beforeExecute.clear()
    ctx.pending_request().with_async_transport(_transport(_json_handler({"d": {"Title": "Contoso"}})))
    ctx.load(ctx.web)

    asyncio.run(ctx.execute_query_async())

    assert ctx.web.properties.get("Title") == "Contoso"


def test_context_execute_query_parallel_async_uses_httpx_transport() -> None:
    seen: list[str] = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen.append(str(request.url))
        return httpx.Response(200, json={"d": {"Title": "Contoso"}})

    ctx = ClientContext("https://contoso.sharepoint.com")
    ctx.pending_request().beforeExecute.clear()
    ctx.pending_request().with_async_transport(_transport(handler))
    for _ in range(3):
        ctx.load(ctx.web)

    asyncio.run(ctx.execute_query_parallel_async(concurrency=3))

    assert len(seen) == 3  # noqa: PLR2004
    assert ctx.web.properties.get("Title") == "Contoso"
