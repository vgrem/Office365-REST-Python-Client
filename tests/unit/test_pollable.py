"""Offline tests for waitable operation entities and Teams async polling.

Covers :mod:`office365.runtime.pollable` (:class:`PollableOperation` plus its
helpers) and the async twin added to ``TeamsAsyncOperation``
(``poll_for_status_async`` / ``wait_for_operation_async``).
"""

from __future__ import annotations

import asyncio
from enum import Enum
from typing import Any

import pytest
from office365.graph_client import GraphClient
from office365.runtime.client_request_exception import ClientRequestException
from office365.runtime.http.request_options import RequestOptions
from office365.runtime.lro import OperationFailedError, OperationStatus, OperationTimeoutError
from office365.runtime.pollable import (
    PollableOperation,
    is_transient_poll_error,
    next_poll_delay,
    normalize_status,
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


class _Status(Enum):
    SUCCEEDED = "succeeded"


# -- pure helpers -----------------------------------------------------------


def test_normalize_status_handles_enum_and_string():
    assert normalize_status(_Status.SUCCEEDED) == "succeeded"
    assert normalize_status("Succeeded") == "succeeded"
    assert normalize_status(" running ") == "running"
    assert normalize_status(None) is None


def test_is_transient_poll_error():
    assert is_transient_poll_error(_not_found())
    assert is_transient_poll_error(ClientRequestException.from_response(_response(503)))
    assert not is_transient_poll_error(ClientRequestException.from_response(_response(500)))


def test_next_poll_delay_honors_retry_after():
    assert next_poll_delay(_response(202, headers={"Retry-After": "7"}), 10) == 7.0  # noqa: PLR2004
    assert next_poll_delay(_response(202), 10) == 10.0  # noqa: PLR2004
    assert next_poll_delay(None, 3) == 3.0  # noqa: PLR2004


# -- PollableOperation.wait / wait_async ------------------------------------


def test_pollable_wait_polls_until_terminal(monkeypatch: pytest.MonkeyPatch):
    clock = _Clock()
    responses = iter(
        [
            _response(202, {"status": "inProgress"}, {"Retry-After": "2"}),
            _response(202, {"status": "completed", "resourceId": "42"}),
        ]
    )
    monkeypatch.setattr("office365.runtime.pollable.reload_operation", lambda op: next(responses))
    op = _FakeOperation({"status": "inProgress"})
    seen: list[str] = []
    result = op.wait(clock=clock.now, sleep=clock.sleep, on_progress=lambda s: seen.append(s.status or ""))
    assert result is op
    assert clock.t == 2.0  # noqa: PLR2004
    assert seen == ["inProgress", "completed"]


def test_pollable_wait_treats_404_as_gap(monkeypatch: pytest.MonkeyPatch):
    clock = _Clock()
    responses: list[Any] = [_not_found(), _response(202, {"status": "completed"})]

    def _reload(_op: Any) -> Any:
        item = responses.pop(0)
        if isinstance(item, Exception):
            raise item
        return item

    monkeypatch.setattr("office365.runtime.pollable.reload_operation", _reload)
    op = _FakeOperation({"status": "notStarted"})
    op.wait(clock=clock.now, sleep=clock.sleep, interval=4)
    assert clock.t == 4.0  # noqa: PLR2004


def test_pollable_wait_raises_on_failed_status(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(
        "office365.runtime.pollable.reload_operation",
        lambda op: _response(202, {"status": "failed", "error": {"code": "x"}}),
    )
    clock = _Clock()
    op = _FakeOperation({"status": "failed"})
    with pytest.raises(OperationFailedError):
        op.wait(clock=clock.now, sleep=clock.sleep)
    # ``raise_on_failure=False`` returns instead of raising
    op.wait(clock=clock.now, sleep=clock.sleep, raise_on_failure=False)
    assert op.is_operation_failed


def test_pollable_wait_times_out(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(
        "office365.runtime.pollable.reload_operation",
        lambda op: _response(202, {"status": "inProgress"}),
    )
    clock = _Clock()
    op = _FakeOperation()
    with pytest.raises(OperationTimeoutError) as excinfo:
        op.wait(clock=clock.now, sleep=clock.sleep, interval=2, timeout=5)
    assert excinfo.value.timeout == 5  # noqa: PLR2004


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


def test_pollable_snapshot_reads_resource_fields():
    op = _FakeOperation({"status": "completed", "resourceId": "r1", "resourceLocation": "https://r"})
    snapshot = op._operation_snapshot()
    assert isinstance(snapshot, OperationStatus)
    assert snapshot.status == "completed"
    assert snapshot.resource_id == "r1"
    assert snapshot.resource_location == "https://r"


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


def test_pollable_stream_yields_snapshots_and_keeps_the_entity(monkeypatch: pytest.MonkeyPatch):
    """A stream is the same loop as ``wait`` — the entity is what ``wait`` returns."""
    responses = iter(
        [
            _response(202, {"status": "running"}, {"Retry-After": "1"}),
            _response(202, {"status": "completed", "resourceId": "42"}),
        ]
    )
    monkeypatch.setattr("office365.runtime.pollable.reload_operation", lambda op: next(responses))
    clock = _Clock()
    op = _FakeOperation({"status": "running"})
    statuses = list(op.stream(clock=clock.now, sleep=clock.sleep))
    assert [s.status for s in statuses] == ["running", "completed"]
    assert statuses[-1].resource_id == "42"
    # The wait is kept, so cancel() can reach it and last_status stays answerable.
    assert op._operation_wait is not None
    assert op._operation_wait.last_status is statuses[-1]
    assert clock.t == 1.0


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


def test_a_404_gap_is_not_reported_to_the_progress_hook(monkeypatch: pytest.MonkeyPatch):
    """The gap is an attempt, not an observation: nothing happened to report."""
    responses: list[Any] = [_not_found(), _response(202, {"status": "completed"})]

    def _reload(_op: Any) -> Any:
        item = responses.pop(0)
        if isinstance(item, Exception):
            raise item
        return item

    monkeypatch.setattr("office365.runtime.pollable.reload_operation", _reload)
    seen: list[str] = []
    op = _FakeOperation({"status": "notStarted"})
    list(
        op.stream(
            clock=_Clock().now, sleep=_Clock().sleep, interval=0, on_progress=lambda s: seen.append(s.status or "")
        )
    )
    assert seen == ["completed"]


def test_pollable_wait_can_be_cancelled():
    """An entity wait is now cancellable: the mixin hands it to the shared engine."""
    op = _FakeOperation({"status": "running"})
    op._operation_wait = _StubWait()
    op.cancel()
    assert op._operation_wait.cancelled  # type: ignore[attr-defined]


class _StubWait:
    cancelled = False

    def cancel(self) -> None:
        self.cancelled = True


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


def test_teams_poll_for_status_waits_for_a_named_status():
    """``status_type`` narrows what "finished" means; a failed status ends it too."""
    client = GraphClient()
    client.pending_request().beforeExecute.clear()
    client.pending_request().transport = ScriptedTransport(
        [_lro(200, {"status": "inProgress"}), _lro(200, {"status": "failed"})]
    )
    operation = client.teams["teamid"].operations["opid"]
    seen: list[str] = []
    operation.poll_for_status(
        TeamsAsyncOperationStatus.inProgress,
        polling_interval=0,
        timeout_sec=30,
        success_callback=lambda _op: seen.append("success"),
    )
    assert seen == ["success"], "the first poll already reported the named status"

    client.pending_request().transport = ScriptedTransport(
        [_lro(200, {"status": "inProgress"}), _lro(200, {"status": "failed"})]
    )
    seen.clear()
    operation.poll_for_status(
        TeamsAsyncOperationStatus.succeeded,
        polling_interval=0,
        timeout_sec=30,
        success_callback=lambda _op: seen.append("success"),
        failure_callback=lambda _op: seen.append("failure"),
    )
    assert seen == ["failure"]


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
