"""Offline tests for ``Prefer: respond-async`` request submission.

Covers :mod:`office365.runtime.respond_async` (``RespondAsyncRequest``), which
bridges the OData ``respond-async`` preference (as used by Excel workbook
operations) onto the generic LRO poller: a ``202 Accepted`` becomes a waitable
``LongRunningOperationResult``, and a synchronous answer becomes one that is
already terminal — either way the caller holds an operation, while a synchronous
response also lands in the query's regular result.
"""

from __future__ import annotations

import asyncio
from typing import Any

import pytest
from office365.graph_client import GraphClient
from office365.runtime.client_request_exception import ClientRequestException
from office365.runtime.client_result import ClientResult
from office365.runtime.lro import LongRunningOperationResult
from office365.runtime.queries.function import FunctionQuery
from office365.runtime.respond_async import RespondAsyncRequest
from tests._scripted_transport import AsyncScriptedTransport, ScriptedTransport

_MONITOR = "https://graph.microsoft.com/v1.0/drives/d1/items/i1/workbook/operations/op1"


def _graph_client(
    *,
    sync_payloads: list[Any] | None = None,
    async_payloads: list[Any] | None = None,
) -> GraphClient:
    client = GraphClient()
    client.pending_request().beforeExecute.clear()
    if sync_payloads is not None:
        client.pending_request().transport = ScriptedTransport(list(sync_payloads))
    if async_payloads is not None:
        client.pending_request()._async_transport = AsyncScriptedTransport(list(async_payloads))
    return client


def _report_query(client: GraphClient) -> tuple[ClientResult[bytes], FunctionQuery]:
    result: ClientResult[bytes] = ClientResult(client, bytes())
    query = FunctionQuery(
        client.reports, "getEmailActivityUserDetail", {"period": "D7"}, result, return_raw_content=True
    )
    return result, query


def _lro(http_status: int, body: Any = None, headers: dict[str, str] | None = None) -> dict[str, Any]:
    payload: dict[str, Any] = {"http_status": http_status}
    if body is not None:
        payload["body"] = body
    if headers is not None:
        payload["headers"] = headers
    return payload


# -- synchronous submission -------------------------------------------------


def test_sync_completion_populates_query_result():
    client = _graph_client(sync_payloads=[_lro(200, b"User,Count\nalice,3\n")])
    result, query = _report_query(client)
    operation = RespondAsyncRequest(client, query).execute()
    assert result.value == b"User,Count\nalice,3\n"
    # The preference was refused: the operation is born terminal, so a caller that
    # opted into the async pattern does not branch on which way the service answered.
    assert operation.is_completed
    assert operation.monitor_url is None
    assert operation.last_status is not None
    assert operation.last_status.http_status == 200  # noqa: PLR2004
    assert operation.last_status.is_success


def test_sync_completion_waits_without_a_request():
    transport = ScriptedTransport([_lro(200, b"csv")])
    client = _graph_client()
    client.pending_request().transport = transport
    _, query = _report_query(client)
    operation = RespondAsyncRequest(client, query).execute()
    status = operation.wait()
    assert status.is_success
    assert [s.status for s in operation.stream()] == ["completed"]
    assert transport.calls == 1  # only the submission; nothing was polled


def test_accepted_returns_pollable_result_and_waits():
    client = _graph_client(
        sync_payloads=[
            _lro(202, headers={"Location": _MONITOR}),
            _lro(202, {"status": "inProgress"}, {"Retry-After": "0"}),
            _lro(200, {"status": "completed", "resourceId": "42"}),
        ]
    )
    result, query = _report_query(client)
    operation = RespondAsyncRequest(client, query).execute()
    assert isinstance(operation, LongRunningOperationResult)
    assert operation.monitor_url == _MONITOR
    status = operation.wait(interval=0.0)
    assert status.is_success
    assert operation.resource_id == "42"
    # The synchronous result must stay untouched on the async path.
    assert result.value == b""


def test_error_status_raises():
    client = _graph_client(sync_payloads=[_lro(403, {"error": {"code": "Forbidden"}})])
    _, query = _report_query(client)
    with pytest.raises(ClientRequestException):
        RespondAsyncRequest(client, query).execute()


# -- asynchronous submission ------------------------------------------------


def test_async_accepted_can_be_polled():
    client = _graph_client(
        async_payloads=[
            _lro(202, headers={"Location": _MONITOR}),
            _lro(200, {"status": "completed", "resourceId": "7"}),
        ]
    )
    _, query = _report_query(client)
    operation = asyncio.run(RespondAsyncRequest(client, query).execute_async())
    assert not operation.is_completed  # accepted: terminal only after polling
    status = asyncio.run(operation.wait_async(interval=0.0))
    assert status.is_success
    assert operation.resource_id == "7"
