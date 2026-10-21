"""Offline tests for the shared polling engine.

Covers :mod:`office365.runtime.operation` — the wait that every long-running
operation in this library is built on. The monitor-URL poller's own behaviour is
covered by ``test_lro.py``; this module tests the base class as a base: what a
subclass supplies, what it inherits, and the two things a family configures as
data (``transient_statuses`` and ``jitter``).
"""

from __future__ import annotations

import asyncio
import threading
import time
from typing import Any

import pytest
from office365.runtime.operation import (
    RETRYABLE_HTTP,
    Operation,
    OperationCancelledError,
    OperationError,
    OperationFailedError,
    OperationStatus,
    OperationTimeoutError,
)


class _Clock:
    """Injectable monotonic clock whose ``sleep`` advances time."""

    def __init__(self) -> None:
        self.t = 0.0
        self.slept: list[float] = []

    def now(self) -> float:
        return self.t

    def sleep(self, seconds: float) -> None:
        self.slept.append(seconds)
        self.t += seconds

    async def asleep(self, seconds: float) -> None:
        self.sleep(seconds)


class _Scripted(Operation[Any]):
    """An operation whose attempts are a script of (status, http_status) pairs."""

    def __init__(self, script: list[tuple[str | None, int]], **options: Any) -> None:
        super().__init__(**options)
        self._script = list(script)
        self.attempts = 0

    def _step(self) -> OperationStatus:
        self.attempts += 1
        status, http_status = self._script.pop(0)
        return OperationStatus(status=status, http_status=http_status)

    async def _step_async(self) -> OperationStatus:
        return self._step()


def _run(script: list[tuple[str | None, int]], **options: Any) -> _Scripted:
    clock = options.pop("clock", None) or _Clock()
    options.setdefault("clock", clock.now)
    options.setdefault("sleep", clock.sleep)
    options.setdefault("async_sleep", clock.asleep)
    operation = _Scripted(script, **options)
    operation.clock = clock  # type: ignore[attr-defined]
    return operation


# -- what a subclass gets from the engine -----------------------------------


def test_stream_yields_every_snapshot_terminal_last():
    operation = _run([("inProgress", 202), ("inProgress", 202), ("completed", 200)])
    statuses = list(operation.stream())
    assert [s.status for s in statuses] == ["inProgress", "inProgress", "completed"]
    assert operation.attempts == 3  # noqa: PLR2004
    assert operation.last_status is statuses[-1]


def test_wait_returns_the_terminal_snapshot():
    status = _run([("inProgress", 202), ("completed", 200)]).wait()
    assert status.status == "completed"
    assert status.is_success


def test_wait_raises_nothing_when_policy_is_off():
    status = _run([("failed", 200)]).wait(raise_on_failure=False)
    assert status.is_failure


def test_wait_raises_the_failure_family():
    with pytest.raises(OperationFailedError):
        _run([("failed", 200)]).wait()
    with pytest.raises(OperationCancelledError):
        _run([("cancelled", 200)]).wait()
    # A cancellation is a failure the caller can tell apart, not a second hierarchy.
    with pytest.raises(OperationError):
        _run([("cancelled", 200)]).wait()


def test_stream_raises_nothing_for_a_failed_outcome():
    """A stream that raises on its last item is a ``wait()`` with extra steps."""
    statuses = list(_run([("failed", 200)]).stream())
    assert len(statuses) == 1
    assert statuses[0].is_failure


def test_outcome_maps_the_terminal_status():
    class _IdOperation(_Scripted):
        def _outcome(self, status: OperationStatus) -> str:
            return "job-7"

    operation = _IdOperation([("completed", 200)], clock=_Clock().now, sleep=_Clock().sleep)
    assert operation.wait() == "job-7"


def test_progress_callback_sees_every_snapshot():
    seen: list[str] = []
    operation = _run([("inProgress", 202), ("completed", 200)], on_progress=lambda s: seen.append(s.status or ""))
    operation.wait()
    assert seen == ["inProgress", "completed"]


def test_per_call_progress_overrides_the_instance_default():
    seen: list[str] = []
    operation = _run([("completed", 200)], on_progress=lambda s: seen.append("default"))
    operation.wait(on_progress=lambda s: seen.append("call"))
    assert seen == ["call"]


# -- the two things a family configures as data ----------------------------


def test_transient_status_means_poll_again_not_an_outcome():
    """A ``404`` on an entity is a gap, not the answer — when the family says so."""
    operation = _run(
        [(None, 404), ("inProgress", 202), ("completed", 200)],
        transient_statuses=frozenset({404, 429, 503}),
    )
    statuses = list(operation.stream())
    assert [s.status for s in statuses] == [None, "inProgress", "completed"]
    assert operation.attempts == 3  # noqa: PLR2004


def test_a_family_can_declare_its_transient_status_is_not_an_observation():
    """Reported by default; a *gap* is a family''s decision, taken by override."""

    class _GapIsSilent(_Scripted):
        def _observable(self, status: OperationStatus) -> bool:
            return status.http_status not in {404}

    clock = _Clock()
    operation = _GapIsSilent(
        [(None, 404), ("inProgress", 202), ("completed", 200)],
        transient_statuses=frozenset({404, 429, 503}),
        clock=clock.now,
        sleep=clock.sleep,
    )
    assert [s.status for s in operation.stream()] == ["inProgress", "completed"]


def test_a_transient_status_outside_the_set_is_terminal():
    """The default set is the monitor-URL one: a ``404`` there is the answer."""
    operation = _run([(None, 404)])
    status = operation.wait(raise_on_failure=False)
    assert status.http_status == 404  # noqa: PLR2004
    assert operation.attempts == 1


def test_default_transient_set_is_the_monitor_one():
    assert RETRYABLE_HTTP == frozenset({429, 503})


def test_jitter_zero_is_exact_and_jitter_spreads():
    exact = _run([("inProgress", 202), ("completed", 200)], interval=10.0)
    exact.wait()
    assert exact.clock.slept == [10.0]  # type: ignore[attr-defined]

    for _ in range(20):
        spread = _run([("inProgress", 202), ("completed", 200)], interval=10.0, jitter=0.2)
        spread.wait()
        delay = spread.clock.slept[0]  # type: ignore[attr-defined]
        assert 8.0 <= delay <= 12.0  # noqa: PLR2004


def test_retry_after_wins_over_the_interval():
    class _RetryAfter(_Scripted):
        def _step(self) -> OperationStatus:
            status = super()._step()
            status.retry_after = 30.0
            return status

    clock = _Clock()
    operation = _RetryAfter([("inProgress", 202), ("completed", 200)], clock=clock.now, sleep=clock.sleep)
    operation.wait()
    assert clock.slept == [30.0]


# -- the deadline ----------------------------------------------------------


def test_timeout_raises_the_shared_error_family():
    """One timeout error for every wait: it is also a ``TimeoutError``."""
    operation = _run([("inProgress", 202)] * 100, interval=10.0, timeout=25.0)
    with pytest.raises(OperationTimeoutError) as caught:
        operation.wait()
    assert caught.value.timeout == 25.0  # noqa: PLR2004
    assert isinstance(caught.value, TimeoutError)
    # Never sleeps past the deadline: the third poll would land at 30s > 25s.
    assert operation.clock.slept == [10.0, 10.0]  # type: ignore[attr-defined]


def test_deadline_counts_time_spent_in_the_attempt():
    """A slow attempt consumes the budget: the deadline is wall time, not poll count."""

    class _Slow(_Scripted):
        def _step(self) -> OperationStatus:
            self.clock.t += 20.0  # type: ignore[attr-defined]
            return super()._step()

    clock = _Clock()
    operation = _Slow([("inProgress", 202)] * 10, clock=clock.now, sleep=clock.sleep, interval=5.0, timeout=25.0)
    operation.clock = clock  # type: ignore[attr-defined]
    with pytest.raises(OperationTimeoutError):
        operation.wait()
    # 20s for the attempt + a 5s pause is 25s: the next pause would exceed it.
    assert operation.attempts == 2  # noqa: PLR2004


def test_per_call_timeout_overrides_the_instance_one():
    operation = _run([("inProgress", 202)] * 10, interval=10.0, timeout=1800.0)
    with pytest.raises(OperationTimeoutError) as caught:
        operation.wait(timeout=15.0)
    assert caught.value.timeout == 15.0  # noqa: PLR2004


# -- cancellation ----------------------------------------------------------


def test_cancel_before_the_first_poll_returns_cancelled():
    operation = _run([("completed", 200)])
    operation.cancel()
    with pytest.raises(OperationCancelledError):
        operation.wait()
    assert operation.attempts == 0


def test_cancel_wakes_a_blocking_wait_from_another_thread():
    """The pause is an event, so a 30 s ``interval`` does not delay a cancel.

    No injected ``sleep``: the default pause is the interruptible one.
    """
    polled = threading.Event()
    raised: list[BaseException] = []

    class _Blocked(Operation[Any]):
        def _step(self) -> OperationStatus:
            polled.set()
            return OperationStatus(status="inProgress", http_status=202)

    operation = _Blocked(interval=30.0)

    def wait() -> None:
        try:
            operation.wait()
        except BaseException as error:  # noqa: BLE001 - asserted below
            raised.append(error)

    thread = threading.Thread(target=wait)
    thread.start()
    assert polled.wait(timeout=5)
    started = time.monotonic()
    operation.cancel()
    thread.join(timeout=5)
    assert not thread.is_alive()
    assert time.monotonic() - started < 1.0  # noqa: PLR2004 - a 30 s pause, not a 30 s wait
    assert isinstance(raised[0], OperationCancelledError)


def test_cancel_does_not_call_the_progress_hook():
    """A synthetic cancellation is not something the service reported."""
    seen: list[str] = []
    operation = _run([("completed", 200)], on_progress=lambda s: seen.append(s.status or ""))
    operation.cancel()
    list(operation.stream())
    assert seen == []


# -- the async twin --------------------------------------------------------


def test_astream_is_the_same_script():
    operation = _run([("inProgress", 202), ("completed", 200)])

    async def collect() -> list[str]:
        return [s.status async for s in operation.astream() if s.status]

    assert asyncio.run(collect()) == ["inProgress", "completed"]


def test_wait_async_returns_the_terminal_snapshot():
    operation = _run([("inProgress", 202), ("completed", 200)])
    status = asyncio.run(operation.wait_async())
    assert status.status == "completed"


def test_wait_async_raises_the_same_family():
    operation = _run([("failed", 200)])
    with pytest.raises(OperationFailedError):
        asyncio.run(operation.wait_async())


def test_cancelled_task_stops_waiting_only_by_default():
    sent: list[str] = []

    class _SendsCancel(_Scripted):
        def _send_cancel(self) -> None:
            sent.append("sync")

        async def _send_cancel_async(self) -> None:
            sent.append("async")

    async def run(**options: Any) -> None:
        operation = _SendsCancel([("inProgress", 202)] * 5, interval=30.0)
        task = asyncio.ensure_future(operation.wait_async(**options))
        await asyncio.sleep(0)
        task.cancel()
        with pytest.raises(asyncio.CancelledError):
            await task

    asyncio.run(run())
    assert sent == []
    asyncio.run(run(cancel_on_task_cancel=True))
    assert sent == ["async"]
