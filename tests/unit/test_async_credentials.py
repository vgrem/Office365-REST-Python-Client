"""Offline tests for awaitable token callbacks (async credentials).

A token callback registered via ``with_access_token`` may be an ``async def``
coroutine function. The async API then awaits it on the event loop (single-flight,
never blocking the loop) and marks the request so the offloaded synchronous auth
hook does not run it again; the synchronous API raises a clear error instead of
failing cryptically. Synchronous callbacks keep their existing offload behaviour.
"""

from __future__ import annotations

import asyncio
import threading
from unittest import mock

import pytest
from office365.graph_client import GraphClient
from office365.runtime.auth.authentication_context import AuthenticationContext as SharePointAuthenticationContext
from office365.runtime.auth.entra.authentication_context import AuthenticationContext as EntraAuthenticationContext
from office365.runtime.odata.v4.batch_request import ODataV4BatchRequest
from office365.runtime.queries.client_query import ClientQuery
from office365.sharepoint.client_context import ClientContext
from tests._scripted_transport import RoutingTransport

_SITE_URL = "https://contoso.sharepoint.com"


def _graph_client(token_callback) -> GraphClient:
    ctx = GraphClient(token_callback=token_callback)
    ctx.pending_request()  # apply the callback to the pending request
    return ctx


def _find_request(transport: RoutingTransport, substring: str):
    return next(r for r in transport.requests if substring in r.url)


# --------------------------------------------------------------------------- #
# Entra / Microsoft Graph
# --------------------------------------------------------------------------- #
def test_entra_acquire_token_async_awaits_callback() -> None:
    calls: list[int] = []

    async def token_cb():
        calls.append(1)
        await asyncio.sleep(0)
        return {"access_token": "tok", "token_type": "Bearer", "expiresIn": 3600}

    auth = EntraAuthenticationContext(tenant="contoso")
    auth.with_access_token(token_cb)

    assert auth.is_async_token_callback is True
    token = asyncio.run(auth.acquire_token_async())

    assert token.accessToken == "tok"
    assert calls == [1]


def test_entra_acquire_token_async_never_overlaps() -> None:
    state = {"active": 0, "max_active": 0, "calls": 0}

    async def token_cb():
        state["calls"] += 1
        state["active"] += 1
        state["max_active"] = max(state["max_active"], state["active"])
        await asyncio.sleep(0.02)
        state["active"] -= 1
        return {"access_token": "tok", "token_type": "Bearer", "expiresIn": 3600}

    auth = EntraAuthenticationContext(tenant="contoso")
    auth.with_access_token(token_cb)

    async def _run():
        return await asyncio.gather(*(auth.acquire_token_async() for _ in range(4)))

    tokens = asyncio.run(_run())

    assert state["max_active"] == 1
    assert all(t.accessToken == "tok" for t in tokens)


def test_graph_async_query_uses_async_token_callback() -> None:
    loop_thread = threading.get_ident()
    seen: dict[str, int] = {}

    async def token_cb():
        seen["thread"] = threading.get_ident()
        return {"access_token": "tok-1", "token_type": "Bearer", "expiresIn": 3600}

    ctx = _graph_client(token_cb)
    transport = RoutingTransport([("", {"displayName": "Ada"})])
    ctx.pending_request().transport = transport

    async def _run():
        return await ctx.me.get().execute_query_async()

    user = asyncio.run(_run())

    assert user.get_property("displayName") == "Ada"
    assert transport.requests[0].headers["Authorization"] == "Bearer tok-1"
    assert seen["thread"] == loop_thread  # awaited on the loop, not offloaded


def test_graph_sync_query_with_async_callback_raises() -> None:
    async def token_cb():
        return {"access_token": "tok", "token_type": "Bearer", "expiresIn": 3600}

    ctx = _graph_client(token_cb)
    ctx.pending_request().transport = RoutingTransport([("", {"displayName": "Ada"})])

    with pytest.raises(RuntimeError, match="async token callback"):
        ctx.me.get().execute_query()


def test_graph_async_query_with_sync_callback_still_offloads() -> None:
    loop_thread = threading.get_ident()
    seen: dict[str, int] = {}

    def token_cb():
        seen["thread"] = threading.get_ident()
        return {"access_token": "sync-tok", "token_type": "Bearer", "expiresIn": 3600}

    ctx = _graph_client(token_cb)
    transport = RoutingTransport([("", {"displayName": "Ada"})])
    ctx.pending_request().transport = transport

    async def _run():
        return await ctx.me.get().execute_query_async()

    asyncio.run(_run())

    assert transport.requests[0].headers["Authorization"] == "Bearer sync-tok"
    assert seen["thread"] != loop_thread  # synchronous callback is offloaded


def test_graph_async_batch_uses_async_token_callback() -> None:
    async def token_cb():
        return {"access_token": "batch-tok", "token_type": "Bearer", "expiresIn": 3600}

    ctx = _graph_client(token_cb)
    ctx.add_query(ClientQuery(ctx))
    transport = RoutingTransport([("", {"responses": [{"id": "0", "status": 200, "headers": {}, "body": {}}]})])
    real_cls = ODataV4BatchRequest

    def _factory(*args, **kwargs):
        batch_request = real_cls(*args, **kwargs)
        batch_request.transport = transport
        return batch_request

    with mock.patch("office365.graph_client.ODataV4BatchRequest", side_effect=_factory):
        asyncio.run(ctx.execute_batch_async(items_per_batch=1))

    assert transport.requests[0].headers["Authorization"] == "Bearer batch-tok"


# --------------------------------------------------------------------------- #
# SharePoint
# --------------------------------------------------------------------------- #
def _digest_payload(value: str = "digest") -> dict:
    return {"d": {"GetContextWebInformation": {"FormDigestValue": value, "FormDigestTimeoutSeconds": 1800}}}


def test_sharepoint_acquire_token_async_caches_single_flight() -> None:
    calls: list[int] = []

    async def token_cb():
        calls.append(1)
        await asyncio.sleep(0.02)
        return {"access_token": "tok", "token_type": "Bearer", "expiresIn": 3600}

    auth = SharePointAuthenticationContext(_SITE_URL)
    auth.with_access_token(token_cb)

    assert auth.is_async_token_callback is True

    async def _run():
        return await asyncio.gather(*(auth.acquire_token_async() for _ in range(4)))

    tokens = asyncio.run(_run())

    assert len(calls) == 1  # cached: refreshed once, not once per awaiter
    assert all(t.accessToken == "tok" for t in tokens)


def test_sharepoint_switching_provider_clears_async_flag() -> None:
    async def token_cb():
        return {"access_token": "tok", "token_type": "Bearer"}

    auth = SharePointAuthenticationContext(_SITE_URL)
    auth.with_access_token(token_cb)
    assert auth.is_async_token_callback is True

    auth.with_cookies({"FedAuth": "x"})

    assert auth.is_async_token_callback is False


def test_sharepoint_async_query_uses_async_token_callback() -> None:
    calls: list[int] = []

    async def token_cb():
        calls.append(1)
        return {"access_token": "sp-tok", "token_type": "Bearer", "expiresIn": 3600}

    ctx = ClientContext(_SITE_URL)
    ctx.with_access_token(token_cb)
    transport = RoutingTransport([("contextInfo", _digest_payload()), ("/_api/Web", {"d": {"Title": "Contoso"}})])
    ctx.pending_request().transport = transport
    ctx.load(ctx.web)

    asyncio.run(ctx.execute_query_async())

    assert ctx.web.properties.get("Title") == "Contoso"
    main = _find_request(transport, "/_api/Web")
    assert main.headers["Authorization"] == "Bearer sp-tok"
    assert main.headers["X-RequestDigest"] == "digest"
    # The digest sub-request reuses the cached token instead of calling the
    # async callback again off-loop.
    assert _find_request(transport, "contextInfo").headers["Authorization"] == "Bearer sp-tok"
    assert calls == [1]


def test_sharepoint_sync_query_with_async_callback_raises() -> None:
    async def token_cb():
        return {"access_token": "sp-tok", "token_type": "Bearer", "expiresIn": 3600}

    ctx = ClientContext(_SITE_URL)
    ctx.with_access_token(token_cb)
    ctx.pending_request().transport = RoutingTransport(
        [("contextInfo", _digest_payload()), ("/_api/web", {"d": {"Title": "Contoso"}})]
    )
    ctx.load(ctx.web)

    with pytest.raises(RuntimeError, match="async token callback"):
        ctx.execute_query()


def test_sharepoint_async_query_survives_a_second_event_loop() -> None:
    # A lock kept across two ``asyncio.run()`` calls binds to the first loop and
    # fails once it is contended, so the context hands out a lock per loop.
    async def token_cb():
        return {"access_token": "sp-tok", "token_type": "Bearer", "expiresIn": 3600}

    ctx = ClientContext(_SITE_URL)
    ctx.with_access_token(token_cb)
    transport = RoutingTransport([("contextInfo", _digest_payload()), ("/_api/Web", {"d": {"Title": "Contoso"}})])
    ctx.pending_request().transport = transport
    ctx.load(ctx.web)

    locks = []

    async def capture():
        locks.append(ctx.authentication_context._get_async_lock())  # noqa: SLF001 - the mechanism under test
        await ctx.execute_query_async()

    asyncio.run(capture())
    asyncio.run(capture())

    assert locks[0] is not locks[1]
