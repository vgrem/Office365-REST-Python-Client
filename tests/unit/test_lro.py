"""Offline tests for the generic long-running-operation (LRO) poller.

Covers :mod:`office365.runtime.lro`: parsing Graph/Azure operation-status
payloads, terminal-state detection, poll-URL resolution
(``Operation-Location`` / ``Azure-AsyncOperation`` / ``Location`` /
``original-url``), ``Retry-After``-driven pacing, throttling retries, failure and
timeout propagation, continuation-token round-tripping, and the awaitable twin
driven through a native-async transport.
"""

from __future__ import annotations

import asyncio
from typing import Any

import pytest
from office365.runtime.http.http_method import HttpMethod
from office365.runtime.http.request_options import RequestOptions
from office365.runtime.lro import (
    ContinuationToken,
    OperationCancelledError,
    OperationFailedError,
    OperationPoller,
    OperationStatus,
    OperationTimeoutError,
    resolve_poll_url,
)
from office365.sharepoint.client_context import ClientContext
from tests._scripted_transport import (
    AsyncScriptedTransport,
    RoutingTransport,
    ScriptedTransport,
    build_response,
)

_MONITOR = "https://api.onedrive.com/monitor/abc"


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


def _ctx() -> ClientContext:
    ctx = ClientContext("https://contoso.sharepoint.com")
    ctx.pending_request().beforeExecute.clear()
    return ctx


def _lro(http_status: int, body: Any = None, headers: dict[str, str] | None = None) -> dict[str, Any]:
    payload: dict[str, Any] = {"http_status": http_status}
    if body is not None:
        payload["body"] = body
    if headers is not None:
        payload["headers"] = headers
    return payload


def _response(http_status: int, body: Any = None, headers: dict[str, str] | None = None) -> Any:
    request = RequestOptions(url=_MONITOR)
    return build_response(request, _lro(http_status, body, headers))


def _poller(transport: Any, clock: _Clock, **kwargs: Any) -> OperationPoller:
    options: dict[str, Any] = {"clock": clock.now, "sleep": clock.sleep, "async_sleep": clock.asleep}
    options.update(kwargs)
    return OperationPoller(_ctx(), _MONITOR, transport=transport, **options)


# -- OperationStatus parsing / classification -------------------------------


def test_status_parses_graph_progress():
    status = OperationStatus.from_response(
        _response(202, {"status": "inProgress", "percentageComplete": 27.8, "resourceLocation": "https://r"})
    )
    assert status.status == "inProgress"
    assert status.http_status == 202  # noqa: PLR2004
    assert status.percentage_complete == 27.8  # noqa: PLR2004
    assert status.resource_location == "https://r"
    assert not status.is_terminal
    assert not status.is_success
    assert not status.is_failure


def test_status_parses_azure_style_payload():
    status = OperationStatus.from_response(_response(200, {"operationStatus": "Succeeded", "percentComplete": 100}))
    # ``operationStatus`` is used when ``status`` is absent and matching is
    # case-insensitive, so Azure's capitalized vocabulary is recognised.
    assert status.status == "Succeeded"
    assert status.percentage_complete == 100.0  # noqa: PLR2004
    assert status.is_success
    assert status.is_terminal


def test_status_completed_terminal_on_202():
    status = OperationStatus.from_response(_response(202, {"status": "completed", "resourceId": "01ABC"}))
    assert status.resource_id == "01ABC"
    assert status.is_success
    assert status.is_terminal


def test_status_failed_terminal():
    status = OperationStatus.from_response(_response(202, {"status": "failed", "error": {"code": "bad"}}))
    assert status.is_failure
    assert status.is_terminal
    assert status.error == {"code": "bad"}


def test_status_200_without_body_is_terminal_success():
    status = OperationStatus.from_response(_response(200))
    assert status.status is None
    assert status.is_success
    assert status.is_terminal


def test_status_202_without_status_is_pending():
    status = OperationStatus.from_response(_response(202))
    assert status.status is None
    assert not status.is_terminal


# -- poll-URL resolution ----------------------------------------------------


def test_resolve_poll_url_precedence():
    resp = _response(
        202,
        {"status": "running"},
        {"Location": "https://l", "Azure-AsyncOperation": "https://a", "Operation-Location": "https://o"},
    )
    assert resolve_poll_url(resp) == "https://o"


def test_resolve_poll_url_final_state_via():
    resp = _response(202, {"status": "running"}, {"Location": "https://l", "Azure-AsyncOperation": "https://a"})
    assert resolve_poll_url(resp, final_state_via="location") == "https://l"
    assert resolve_poll_url(resp, final_state_via="azure-async-operation") == "https://a"
    assert resolve_poll_url(resp, final_state_via="original-url", original_url="https://orig") == "https://orig"


def test_resolve_poll_url_unknown_mode():
    resp = _response(202, {"status": "running"}, {"Location": "https://l"})
    with pytest.raises(ValueError, match="Unknown final_state_via"):
        resolve_poll_url(resp, final_state_via="nope")


def test_from_response_requires_monitor_url():
    with pytest.raises(ValueError, match="monitor URL"):
        OperationPoller.from_response(_ctx(), _response(200))


def test_from_response_builds_poller():
    resp = _response(202, {"status": "running"}, {"Location": _MONITOR})
    poller = OperationPoller.from_response(_ctx(), resp)
    assert poller.poll_url == _MONITOR
    assert poller.final_state_via == "auto"
    assert poller.last_status is None


# -- synchronous polling ----------------------------------------------------


def test_wait_returns_on_completed_status():
    clock = _Clock()
    transport = ScriptedTransport(
        [
            _lro(202, {"status": "inProgress", "percentageComplete": 10}, {"Retry-After": "1"}),
            _lro(202, {"status": "completed", "resourceId": "42"}),
        ]
    )
    poller = _poller(transport, clock)
    seen: list[OperationStatus] = []
    status = poller.wait(on_progress=seen.append)
    assert status.is_success and status.resource_id == "42"
    assert transport.calls == 2  # noqa: PLR2004
    assert [s.status for s in seen] == ["inProgress", "completed"]
    assert clock.t == 1.0  # the Retry-After gap was honored
    assert poller.last_status is status


def test_wait_uses_interval_when_no_retry_after():
    clock = _Clock()
    transport = ScriptedTransport([_lro(202, {"status": "inProgress"}), _lro(202, {"status": "completed"})])
    poller = _poller(transport, clock, interval=3)
    poller.wait()
    assert clock.t == 3.0  # noqa: PLR2004


def test_wait_retries_throttled_status():
    clock = _Clock()
    transport = ScriptedTransport(
        [
            _lro(503, {"error": {"code": "busy"}}, {"Retry-After": "2"}),
            _lro(202, {"status": "completed"}),
        ]
    )
    poller = _poller(transport, clock)
    status = poller.wait()
    assert status.is_success
    assert transport.calls == 2  # noqa: PLR2004
    assert clock.t == 2.0  # noqa: PLR2004


def test_wait_raises_on_failure():
    transport = ScriptedTransport([_lro(202, {"status": "failed", "error": {"code": "x"}})])
    poller = _poller(transport, _Clock())
    with pytest.raises(OperationFailedError) as excinfo:
        poller.wait()
    assert excinfo.value.status.status == "failed"


def test_wait_can_return_failure_status():
    transport = ScriptedTransport([_lro(202, {"status": "failed", "error": {"code": "x"}})])
    status = _poller(transport, _Clock()).wait(raise_on_failure=False)
    assert status.is_failure


def test_wait_times_out():
    clock = _Clock()
    transport = ScriptedTransport([_lro(202, {"status": "inProgress"}) for _ in range(10)])
    poller = _poller(transport, clock, interval=2, timeout=5)
    with pytest.raises(OperationTimeoutError) as excinfo:
        poller.wait()
    assert excinfo.value.timeout == 5  # noqa: PLR2004
    # two 2s gaps elapse, then the third poll would exceed the deadline
    assert clock.t == 4.0  # noqa: PLR2004


def test_wait_raises_client_exception_on_permanent_error():
    from office365.runtime.client_request_exception import ClientRequestException

    transport = ScriptedTransport([_lro(404, {"error": {"code": "gone"}})])
    with pytest.raises(ClientRequestException):
        _poller(transport, _Clock()).wait()


def test_instance_progress_callback_is_used():
    transport = ScriptedTransport([_lro(202, {"status": "completed"})])
    seen: list[str] = []
    poller = _poller(transport, _Clock(), on_progress=lambda s: seen.append(s.status or ""))
    poller.wait()
    assert seen == ["completed"]


# -- continuation tokens ----------------------------------------------------


def test_continuation_token_round_trip():
    transport = ScriptedTransport([_lro(202, {"status": "completed"})])
    poller = _poller(transport, _Clock(), final_state_via="location")
    poller.wait()
    token = poller.to_continuation_token()
    assert token.status == "completed"

    restored = OperationPoller.from_continuation_token(_ctx(), token.to_json())
    assert restored.poll_url == _MONITOR
    assert restored.final_state_via == "location"

    from_mapping = ContinuationToken.from_json({"poll_url": _MONITOR})
    assert from_mapping.status is None
    assert from_mapping.final_state_via == "auto"


def test_continuation_token_invalid():
    with pytest.raises(ValueError, match="Invalid continuation token"):
        ContinuationToken.from_json("{}")


# -- asynchronous polling ---------------------------------------------------


def test_wait_async_completes():
    clock = _Clock()
    transport = AsyncScriptedTransport(
        [
            _lro(202, {"status": "inProgress"}, {"Retry-After": "1"}),
            _lro(202, {"status": "completed", "resourceId": "9"}),
        ]
    )
    poller = OperationPoller(
        _ctx(),
        _MONITOR,
        async_transport=transport,
        clock=clock.now,
        async_sleep=clock.asleep,
    )
    status = asyncio.run(poller.wait_async())
    assert status.is_success and status.resource_id == "9"
    assert transport.calls == 2  # noqa: PLR2004
    assert clock.t == 1.0


def test_wait_async_retries_throttled_status():
    clock = _Clock()
    transport = AsyncScriptedTransport(
        [
            _lro(429, {"error": {"code": "throttled"}}, {"Retry-After": "4"}),
            _lro(202, {"status": "succeeded"}),
        ]
    )
    poller = OperationPoller(
        _ctx(),
        _MONITOR,
        async_transport=transport,
        clock=clock.now,
        async_sleep=clock.asleep,
    )
    status = asyncio.run(poller.wait_async())
    assert status.is_success
    assert clock.t == 4.0  # noqa: PLR2004


# -- cancellation -----------------------------------------------------------


def test_status_cancelled_is_recognized():
    status = OperationStatus.from_response(_response(202, {"status": "Cancelled"}))
    assert status.is_cancelled
    assert status.is_terminal
    # Cancelled stays a failure for backward compatibility; is_cancelled distinguishes.
    assert status.is_failure
    assert not status.is_success


def test_wait_raises_cancelled_error():
    transport = ScriptedTransport([_lro(202, {"status": "cancelled"})])
    with pytest.raises(OperationCancelledError) as excinfo:
        _poller(transport, _Clock()).wait()
    assert excinfo.value.status.is_cancelled
    # OperationCancelledError is an OperationFailedError, so old handlers still catch it.
    assert isinstance(excinfo.value, OperationFailedError)


def test_wait_can_return_cancelled_status():
    transport = ScriptedTransport([_lro(202, {"status": "cancelled"})])
    status = _poller(transport, _Clock()).wait(raise_on_failure=False)
    assert status.is_cancelled


def test_cancel_before_wait_raises_without_polling():
    transport = ScriptedTransport([_lro(202, {"status": "completed"})])
    poller = _poller(transport, _Clock())
    poller.cancel()
    with pytest.raises(OperationCancelledError):
        poller.wait()
    assert transport.calls == 0


def test_cancel_stops_wait_at_poll_boundary():
    clock = _Clock()
    transport = ScriptedTransport([_lro(202, {"status": "inProgress"}), _lro(202, {"status": "completed"})])
    holder: dict[str, OperationPoller] = {}

    def sleepy(_seconds: float) -> None:
        holder["poller"].cancel()  # simulate another thread cancelling mid-wait

    poller = OperationPoller(_ctx(), _MONITOR, transport=transport, clock=clock.now, sleep=sleepy)
    holder["poller"] = poller
    with pytest.raises(OperationCancelledError):
        poller.wait()
    assert transport.calls == 1


def test_cancel_sends_service_request():
    clock = _Clock()
    cancel_url = "https://api.onedrive.com/operations/abc"
    transport = RoutingTransport(
        [
            (_MONITOR, _lro(202, {"status": "inProgress"})),
            (cancel_url, {"http_status": 204}),
        ]
    )
    cancel_request = RequestOptions(url=cancel_url, method=HttpMethod.Post)
    poller = OperationPoller(
        _ctx(),
        _MONITOR,
        transport=transport,
        cancel_request=cancel_request,
        clock=clock.now,
        sleep=clock.sleep,
    )
    poller.cancel()
    assert transport.calls == [cancel_url]


def test_wait_async_stops_when_cancelled():
    clock = _Clock()
    transport = AsyncScriptedTransport([_lro(202, {"status": "completed"})])
    poller = OperationPoller(_ctx(), _MONITOR, async_transport=transport, clock=clock.now, async_sleep=clock.asleep)
    poller.cancel()
    with pytest.raises(OperationCancelledError):
        asyncio.run(poller.wait_async())
    assert transport.calls == 0


def test_wait_async_forwards_cancel_on_task_cancel():
    clock = _Clock()
    transport = AsyncScriptedTransport([_lro(202, {"status": "inProgress"}), {"http_status": 204}])
    cancel_request = RequestOptions(url="https://api.onedrive.com/operations/abc", method=HttpMethod.Post)

    async def asleep(_seconds: float) -> None:
        raise asyncio.CancelledError

    poller = OperationPoller(
        _ctx(),
        _MONITOR,
        async_transport=transport,
        cancel_request=cancel_request,
        clock=clock.now,
        async_sleep=asleep,
    )
    with pytest.raises(asyncio.CancelledError):
        asyncio.run(poller.wait_async(cancel_on_task_cancel=True))
    assert transport.calls == 2  # noqa: PLR2004 - one poll + one cancel request


def test_wait_async_task_cancel_does_not_forward_by_default():
    clock = _Clock()
    transport = AsyncScriptedTransport([_lro(202, {"status": "inProgress"})])
    cancel_request = RequestOptions(url="https://api.onedrive.com/operations/abc", method=HttpMethod.Post)

    async def asleep(_seconds: float) -> None:
        raise asyncio.CancelledError

    poller = OperationPoller(
        _ctx(),
        _MONITOR,
        async_transport=transport,
        cancel_request=cancel_request,
        clock=clock.now,
        async_sleep=asleep,
    )
    with pytest.raises(asyncio.CancelledError):
        asyncio.run(poller.wait_async())
    assert transport.calls == 1
