"""Offline tests for waitable operation entities and Teams async polling.

Covers :mod:`office365.runtime.pollable` (:class:`PollableOperation` plus its
helpers) and the async twin added to ``TeamsAsyncOperation``
(``poll_for_status_async`` / ``wait_for_operation_async``).
"""

from __future__ import annotations

import asyncio
from typing import Any

import pytest
from office365.graph_client import GraphClient
from office365.runtime.client_request_exception import ClientRequestException
from office365.runtime.http.request_options import RequestOptions
from office365.runtime.lro import OperationFailedError
from office365.runtime.pollable import (
    PollableOperation,
    is_transient_poll_error,
    next_poll_delay,
)
from office365.teams.operations.async_operation import wait_for_operation_async
from office365.teams.operations.async_status import TeamsAsyncOperationStatus
from tests._scripted_transport import AsyncScriptedTransport, ScriptedTransport, build_response

_URL = "https://graph.microsoft.com/v1.0/sites/root/operations/1"


class _Clock:
    """Injectable monotonic clock whose ``sleep`` advances time."""

    def __init__(self) -> None:
        self.t = 0.0

    def now(self) -> float:
        return self.t

    def sleep(self, seconds: float) -> None:
        self.t += seconds

    async def asleep(self, seconds: float) -> None:
        self.t += seconds


def _lro(http_status: int, body: Any = None, headers: dict[str, str] | None = None) -> dict[str, Any]:
    payload: dict[str, Any] = {"http_status": http_status}
    if body is not None:
        payload["body"] = body
    if headers is not None:
        payload["headers"] = headers
    return payload


def _response(http_status: int, body: Any = None, headers: dict[str, str] | None = None) -> Any:
    return build_response(RequestOptions(url=_URL), _lro(http_status, body, headers))


def _not_found() -> ClientRequestException:
    return ClientRequestException.from_response(_response(404, {"error": {"code": "NotFound"}}))


class _FakeOperation(PollableOperation):
    """Minimal host exposing just ``properties`` (the mixin's only runtime need)."""

    def __init__(self, properties: dict[str, Any] | None = None) -> None:
        self.properties = properties or {}


# -- pure helpers -----------------------------------------------------------


def test_is_transient_poll_error():
    assert is_transient_poll_error(_not_found())
    assert is_transient_poll_error(ClientRequestException.from_response(_response(503)))
    assert not is_transient_poll_error(ClientRequestException.from_response(_response(500)))


def test_next_poll_delay_honors_retry_after():
    assert next_poll_delay(_response(202, headers={"Retry-After": "7"}), 10) == 7.0  # noqa: PLR2004
    assert next_poll_delay(_response(202), 10) == 10.0  # noqa: PLR2004
    assert next_poll_delay(None, 3) == 3.0  # noqa: PLR2004


# -- PollableOperation.wait / wait_async ------------------------------------


def test_pollable_wait_async_completes(monkeypatch: pytest.MonkeyPatch):
    clock = _Clock()
    responses = iter(
        [
            _response(202, {"status": "running"}, {"Retry-After": "1"}),
            _response(202, {"status": "succeeded"}),
        ]
    )

    async def _reload(_op: Any) -> Any:
        return next(responses)

    monkeypatch.setattr("office365.runtime.pollable.reload_operation_async", _reload)
    op = _FakeOperation({"status": "running"})
    result = asyncio.run(op.wait_async(clock=clock.now, async_sleep=clock.asleep))
    assert result is op
    assert clock.t == 1.0


def test_pollable_completion_helpers():
    assert _FakeOperation({"status": "completed"}).is_operation_complete
    assert not _FakeOperation({"status": "completed"}).is_operation_failed
    assert _FakeOperation({"status": "failed"}).is_operation_failed
    assert not _FakeOperation({"status": "running"}).is_operation_complete


# -- real entities through the request pipeline -----------------------------


def test_rich_long_running_operation_wait():
    client = GraphClient()
    client.pending_request().beforeExecute.clear()
    client.pending_request().transport = ScriptedTransport(
        [
            _lro(200, {"status": "running"}),
            _lro(200, {"status": "completed", "resourceId": "res", "resourceLocation": "https://loc"}),
        ]
    )
    operation = client.sites["root"].operations["op1"]
    operation.wait(interval=0)
    assert operation.properties["status"] == "completed"
    assert operation.resource_id == "res"
    assert operation.resource_location == "https://loc"


def test_pollable_stream_raises_nothing_for_a_failed_outcome(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(
        "office365.runtime.pollable.reload_operation",
        lambda op: _response(202, {"status": "failed", "error": {"code": "x"}}),
    )
    op = _FakeOperation({"status": "failed"})
    statuses = list(op.stream(clock=_Clock().now, sleep=_Clock().sleep))
    assert len(statuses) == 1
    assert statuses[0].is_failure
    with pytest.raises(OperationFailedError):
        op.wait(clock=_Clock().now, sleep=_Clock().sleep)


def test_teams_poll_for_status_blocks_until_succeeded():
    """The sync twin polls to completion itself instead of queueing a callback chain."""
    client = GraphClient()
    client.pending_request().beforeExecute.clear()
    client.pending_request().transport = ScriptedTransport(
        [
            _lro(404, {"error": {"code": "NotFound", "message": "not created yet"}}),
            _lro(200, {"status": "inProgress"}),
            _lro(200, {"status": "succeeded", "targetResourceId": "t1"}),
        ]
    )
    operation = client.teams["teamid"].operations["opid"]
    seen: list[str] = []

    result = operation.poll_for_status(
        polling_interval=0, timeout_sec=30, success_callback=lambda _op: seen.append("success")
    )

    assert result is operation
    assert seen == ["success"]
    assert operation.target_resource_id == "t1"
    assert client.pending_request().transport.calls == 3  # noqa: PLR2004 - 404 gap, then two polls


# -- Teams async polling ----------------------------------------------------


def _teams_client(payloads: list[Any]) -> GraphClient:
    client = GraphClient()
    client.pending_request().beforeExecute.clear()
    client.pending_request()._async_transport = AsyncScriptedTransport(payloads)
    return client


def test_teams_poll_for_status_async_succeeds_with_404_gap():
    client = _teams_client(
        [
            _lro(404, {"error": {"code": "NotFound", "message": "not created yet"}}),
            _lro(200, {"status": "succeeded", "targetResourceId": "t1"}),
        ]
    )
    operation = client.teams["teamid"].operations["opid"]
    seen: list[str] = []
    result = asyncio.run(
        operation.poll_for_status_async(
            TeamsAsyncOperationStatus.succeeded,
            timeout_sec=30,
            polling_interval=0,
            success_callback=lambda _op: seen.append("success"),
            failure_callback=lambda _op: seen.append("failure"),
        )
    )
    assert result is operation
    assert seen == ["success"]
    assert operation.operation_status == "succeeded"


def test_teams_poll_for_status_async_reports_failure():
    client = _teams_client([_lro(200, {"status": "failed", "error": {"code": "bad"}})])
    operation = client.teams["teamid"].operations["opid"]
    seen: list[str] = []
    asyncio.run(
        operation.poll_for_status_async(
            TeamsAsyncOperationStatus.succeeded,
            timeout_sec=30,
            polling_interval=0,
            failure_callback=lambda _op: seen.append("failure"),
        )
    )
    assert seen == ["failure"]


def test_teams_poll_for_status_async_times_out():
    client = _teams_client([_lro(200, {"status": "running"})])
    operation = client.teams["teamid"].operations["opid"]
    seen: list[str] = []
    asyncio.run(
        operation.poll_for_status_async(
            TeamsAsyncOperationStatus.succeeded,
            timeout_sec=0,
            polling_interval=0,
            failure_callback=lambda _op: seen.append("timeout"),
        )
    )
    assert seen == ["timeout"]


def test_wait_for_operation_async_raises_on_failure():
    client = _teams_client([_lro(200, {"status": "failed"})])
    operation = client.teams["teamid"].operations["opid"]
    with pytest.raises(RuntimeError, match="Async operation failed"):
        asyncio.run(wait_for_operation_async(operation, timeout_sec=30, interval=0))
