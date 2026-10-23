"""Offline tests for the deferred ``ClientObject.get_or_none``.

Like ``get()`` the helper must only *queue* a read — never touch the wire. When
the entity is missing (HTTP 404 / ``Request_ResourceNotFound``) the error is
swallowed and the returned object is left uninitialized; other failures still
propagate.
"""

from __future__ import annotations

import asyncio

import pytest
from office365.graph_client import GraphClient
from office365.runtime.client_request_exception import ClientRequestException
from tests._scripted_transport import AsyncScriptedTransport, ScriptedTransport

_NOT_FOUND = {
    "http_status": 404,
    "body": {"error": {"code": "Request_ResourceNotFound", "message": "Resource not found"}},
}

_FORBIDDEN = {
    "http_status": 403,
    "body": {"error": {"code": "Forbidden", "message": "Access is denied."}},
}


def _client(payloads):
    transport = ScriptedTransport(payloads)
    client = GraphClient()
    client.pending_request().beforeExecute.clear()
    client.pending_request().transport = transport
    return client, transport


def test_get_or_none_defers_until_execute():
    client, transport = _client([{"id": "t1", "displayName": "Team One"}])

    team = client.teams["t1"].get_or_none()

    # a deferred builder must not hit the wire on its own
    assert transport.calls == 0
    assert not team.is_loaded

    team.execute_query()

    assert transport.calls == 1
    assert team.is_loaded
    assert team.get_property("id") == "t1"


def test_get_or_none_propagates_non_404_errors():
    client, _ = _client([_FORBIDDEN])

    team = client.teams["t1"].get_or_none()

    with pytest.raises(ClientRequestException):
        team.execute_query()

    assert not team.is_loaded


def _async_client(payloads):
    transport = AsyncScriptedTransport(payloads)
    client = GraphClient()
    client.pending_request().beforeExecute.clear()
    client.pending_request()._async_transport = transport
    return client, transport


def test_get_or_none_async_defers_and_tolerates_404():
    client, transport = _async_client([_NOT_FOUND])

    async def _run():
        team = client.teams["missing-team"].get_or_none()
        assert transport.calls == 0  # still deferred
        await team.execute_query_async()
        return team

    team = asyncio.run(_run())

    assert not team.is_loaded
    assert transport.calls == 1
