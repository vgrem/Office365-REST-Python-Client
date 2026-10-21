"""One polling engine for every long-running operation this library knows about.

Microsoft 365 models long-running work in four shapes, and they differ only in *what
one poll is* — not in how a wait behaves:

===========================  ============================================  ================
shape                        one poll                                      result of ``wait``
===========================  ============================================  ================
monitor URL                  ``GET`` an unauthenticated status document     status snapshot
operation entity             re-read the entity (``GET`` its own URL)       the entity
service job counter          call a ``status_fn`` returning a tuple         the status string
async-operation entity       re-read, waiting for one status               the entity
===========================  ============================================  ================

Everything else is the same: a deadline, ``Retry-After`` pacing, a progress hook, a
cooperative cancel, and the rule that a stream yields snapshots and raises nothing.
So this module owns the wait — :class:`Operation` — and a subclass supplies
:meth:`Operation._step` (one attempt) and optionally
:meth:`Operation._send_cancel` (the service-specific cancel). Before this, each family
had its own loop, and they disagreed: only the monitor-URL poller could be cancelled or
streamed, only the entity mixin tolerated a ``404`` gap, and the migration monitor's
deadline did not count the time its own requests took (it added ``interval`` per
iteration and ignored request duration, so a slow endpoint could poll past its
timeout indefinitely).

The lifecycle a caller sees is always the same three forms:

- :meth:`Operation.stream` / :meth:`Operation.astream` — every snapshot, nothing raised
  for a failed or cancelled outcome;
- :meth:`Operation.wait` / :meth:`Operation.wait_async` — the same loop with the failure
  policy applied (``raise_on_failure``), returning ``_outcome(status)``;
- :meth:`Operation.cancel` / :meth:`Operation.cancel_async` — stop waiting at the next
  poll boundary, and ask the service to stop too when the operation has a cancel request.

Cancellation is **not** a rollback: whatever the service already applied remains.
"""

from __future__ import annotations

import asyncio
import json
import random
import threading
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, AsyncIterator, Awaitable, Callable, Generic, Iterator, TypeVar, cast

from requests import Response

from office365.runtime.retry import response_retry_after

#: Response headers that may carry the operation-status URL, in resolution order.
POLL_URL_HEADERS = ("Operation-Location", "Azure-AsyncOperation", "Location")

_HEADER_BY_FINAL_STATE = {
    "location": "Location",
    "operation-location": "Operation-Location",
    "azure-async-operation": "Azure-AsyncOperation",
}

#: Operation statuses that mean the work finished successfully.
SUCCESS_STATUSES = frozenset({"completed", "succeeded", "success", "finished"})

#: Operation statuses that mean the work finished with a failure.
FAILURE_STATUSES = frozenset({"failed", "failure", "cancelled", "canceled", "error"})

#: Operation statuses that mean the work was cancelled rather than failed.
CANCELLED_STATUSES = frozenset({"cancelled", "canceled"})

#: Operation statuses that mean the work finished, but not all of it succeeded.
#:
#: SharePoint and Graph report ``partiallySucceeded`` for a copy/migration job
#: whose failures were item-level. It is *terminal* — polling again will not make
#: it better — so it must stop the wait, but it is neither a success nor a
#: failure of the operation as a whole.
PARTIAL_STATUSES = frozenset({"partiallysucceeded", "partiallysuccessful", "partiallycompleted"})

#: HTTP statuses that ask a monitor-URL client to back off and poll again.
RETRYABLE_HTTP = frozenset({429, 503})

_PENDING_HTTP = 202

#: Callback invoked with the latest :class:`OperationStatus` on every poll.
OperationCallback = Callable[["OperationStatus"], None]

#: What a finished wait hands back: a status snapshot, an entity, a status string.
T = TypeVar("T")


def _parse_json(response: Response) -> Any:
    """Parse ``response`` as JSON, returning ``None`` when it isn't JSON."""
    content_type = (getattr(response, "headers", None) or {}).get("Content-Type", "")
    if "json" not in content_type.lower():
        return None
    try:
        return response.json()
    except (TypeError, ValueError):
        return None


def _first(data: Any, *keys: str) -> Any:
    """Return the first present, non-null value among ``keys`` of a mapping."""
    if not isinstance(data, dict):
        return None
    for key in keys:
        value = data.get(key)
        if value is not None:
            return value
    return None


def _percentage(data: Any) -> float | None:
    """Read ``percentageComplete`` (Graph) / ``percentComplete`` (Azure)."""
    value = _first(data, "percentageComplete", "percentComplete")
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _timestamp(data: Any, *keys: str) -> datetime | None:
    """Read an ISO-8601 stamp, timezone-aware (an offset-less value is read as UTC)."""
    raw = _first(data, *keys)
    if not isinstance(raw, str) or not raw:
        return None
    try:
        value = datetime.fromisoformat(raw.replace("Z", "+00:00"))
    except ValueError:
        return None
    return value if value.tzinfo is not None else value.replace(tzinfo=timezone.utc)


@dataclass
class OperationStatus:
    """A single snapshot of a long-running operation.

    Attributes:
        status: Server-reported status (``inProgress``, ``completed`` ...), or
            ``None`` when the response carries no status body.
        http_status: HTTP status of the poll response.
        percentage_complete: Completion percentage (0-100) when reported.
        resource_id: Identifier of the produced/modified resource, when reported.
        resource_location: URL of the produced/modified resource (or final result).
        created_date_time: When the operation was created, timezone-aware (UTC
            when the service sends no offset).
        last_action_date_time: When the operation last changed — the anchor for
            stall detection (``now - last_action_date_time``).
        retry_after: Seconds this poll response asked the client to wait, when it
            sent ``Retry-After``.
        error: Error payload when the operation failed.
        response: The raw terminal/poll response (carries the result body, e.g. a
            report export), excluded from ``repr``.
    """

    status: str | None = None
    http_status: int = 0
    percentage_complete: float | None = None
    resource_id: str | None = None
    resource_location: str | None = None
    created_date_time: datetime | None = None
    last_action_date_time: datetime | None = None
    retry_after: float | None = None
    error: Any = None
    response: Response | None = field(default=None, repr=False)

    @classmethod
    def from_response(cls, response: Response) -> "OperationStatus":
        """Build a snapshot from a poll response."""
        data = _parse_json(response)
        retry_after = response_retry_after(response)
        return cls(
            status=_first(data, "status", "operationStatus"),
            http_status=int(getattr(response, "status_code", 0) or 0),
            percentage_complete=_percentage(data),
            resource_id=_first(data, "resourceId"),
            resource_location=_first(data, "resourceLocation", "targetResourceLocation"),
            created_date_time=_timestamp(data, "createdDateTime"),
            last_action_date_time=_timestamp(data, "lastActionDateTime"),
            retry_after=None if retry_after is None else float(retry_after),
            error=_first(data, "error"),
            response=response,
        )

    @property
    def _status_key(self) -> str | None:
        """Lower-cased status, so Graph (``completed``) and Azure (``Succeeded``) both match."""
        return self.status.strip().lower() if isinstance(self.status, str) else None

    @property
    def is_success(self) -> bool:
        """Whether the operation finished successfully."""
        key = self._status_key
        if key is not None:
            return key in SUCCESS_STATUSES
        return self.http_status != _PENDING_HTTP and 200 <= self.http_status < 300  # noqa: PLR2004

    @property
    def is_failure(self) -> bool:
        """Whether the operation finished with a failure."""
        key = self._status_key
        if key is not None:
            return key in FAILURE_STATUSES
        return self.http_status >= 400  # noqa: PLR2004

    @property
    def is_partially_succeeded(self) -> bool:
        """Whether the operation finished with some item-level failures.

        Terminal, and neither :attr:`is_success` nor :attr:`is_failure`: the work
        stopped, most of it succeeded, and ``wait()`` returns instead of raising.
        Inspect :attr:`error` (or the service-specific report) for what failed.
        """
        return self._status_key in PARTIAL_STATUSES

    @property
    def is_cancelled(self) -> bool:
        """Whether the operation was cancelled (by the caller or the service).

        Cancellation is terminal and **not** a rollback: whatever the service
        already applied remains. A cancelled status also reports
        :attr:`is_failure` for backward compatibility — use this property to
        tell the two apart.
        """
        return self._status_key in CANCELLED_STATUSES

    @property
    def is_terminal(self) -> bool:
        """Whether no further polling is needed.

        A ``3xx`` (redirect to the final result), a known success/failure status,
        or a non-``202`` response without a status body is terminal; a ``202``
        with an in-progress/unknown status is not.
        """
        if 300 <= self.http_status < 400:  # noqa: PLR2004
            return True
        key = self._status_key
        if key is not None:
            return key in SUCCESS_STATUSES or key in FAILURE_STATUSES or key in PARTIAL_STATUSES
        return self.http_status != _PENDING_HTTP


def resolve_poll_url(
    response: Response,
    *,
    final_state_via: str = "auto",
    original_url: str | None = None,
) -> str | None:
    """Resolve the operation-status (monitor) URL from a ``202`` response.

    ``final_state_via="auto"`` (default) returns the first header present among
    :data:`POLL_URL_HEADERS`. The explicit values select a single header, mirroring
    ``azure-core``; ``"original-url"`` polls the original request URL instead
    (pass it as ``original_url``).
    """
    if final_state_via == "original-url":
        return original_url
    headers = getattr(response, "headers", None) or {}
    if final_state_via != "auto":
        header = _HEADER_BY_FINAL_STATE.get(final_state_via)
        if header is None:
            raise ValueError(f"Unknown final_state_via: {final_state_via!r}")
        return headers.get(header)
    for header in POLL_URL_HEADERS:
        value = headers.get(header)
        if value:
            return value
    return None


@dataclass
class ContinuationToken:
    """Serializable pointer that lets an operation be resumed later.

    Captures the monitor URL and the poll-URL resolution mode so a restarted
    process (or a later call) can continue polling the same operation with
    :meth:`OperationPoller.from_continuation_token`.
    """

    poll_url: str
    final_state_via: str = "auto"
    status: str | None = None

    def to_json(self) -> str:
        """Serialize the token to JSON."""
        return json.dumps({"poll_url": self.poll_url, "final_state_via": self.final_state_via, "status": self.status})

    @classmethod
    def from_json(cls, value: str | bytes | dict[str, Any]) -> "ContinuationToken":
        """Rebuild a token from :meth:`to_json` output (or an equivalent mapping)."""
        data = json.loads(value) if isinstance(value, (str, bytes)) else value
        if not isinstance(data, dict) or not data.get("poll_url"):
            raise ValueError("Invalid continuation token")
        return cls(
            poll_url=str(data["poll_url"]),
            final_state_via=str(data.get("final_state_via", "auto")),
            status=data.get("status"),
        )


class OperationError(Exception):
    """Base class for long-running-operation polling errors."""


class OperationFailedError(OperationError):
    """Raised when a polled operation reaches a failed terminal status."""

    def __init__(self, status: OperationStatus) -> None:
        self.status = status
        super().__init__(f"Long-running operation failed: status={status.status!r}, error={status.error!r}")


class OperationCancelledError(OperationFailedError):
    """Raised when a polled operation reaches a cancelled terminal status.

    A subclass of :class:`OperationFailedError` so existing handlers keep
    working; check :attr:`OperationStatus.is_cancelled` to distinguish a
    cancellation from a failure.
    """

    def __init__(self, status: OperationStatus) -> None:
        self.status = status
        OperationError.__init__(self, f"Long-running operation was cancelled: status={status.status!r}")


class OperationTimeoutError(OperationError, TimeoutError):
    """Raised when an operation does not finish before the timeout.

    Also a :class:`TimeoutError`, so code written against the other waits in this
    library (``except TimeoutError``) keeps working.
    """

    def __init__(self, timeout: float) -> None:
        self.timeout = timeout
        super().__init__(f"Timed out after {timeout}s waiting for the long-running operation")


class Operation(Generic[T]):
    """The wait: poll :meth:`_step` until it reports a terminal status.

    A subclass supplies one attempt, sync and async, and says which HTTP statuses
    mean "the service is busy, try again" rather than "this is the answer":

    ```python
    class MyOperation(Operation):
        def _step(self) -> OperationStatus: ...
        async def _step_async(self) -> OperationStatus: ...
    ```

    Everything a caller sees — :meth:`stream`, :meth:`wait`, :meth:`astream`,
    :meth:`wait_async`, :meth:`cancel` — is implemented once, here.

    Args:
        interval: Seconds between polls when the attempt sends no ``Retry-After``.
        timeout: Maximum seconds to wait before raising
            :class:`OperationTimeoutError`.
        on_progress: Optional default callback, invoked with each snapshot.
        transient_statuses: HTTP statuses that mean "poll again", not an outcome
            (``429``/``503`` for a monitor URL; ``404`` too for an entity that a
            service publishes a moment after accepting the work).
        jitter: Fraction of the delay to spread (``0.2`` = up to ±20%), so many
            clients polling one endpoint do not synchronise. ``0.0`` is exact.
        clock: Injectable monotonic clock (tests).
        sleep: Override the wait between polls. By default the engine waits on an
            internal event, so :meth:`cancel` wakes a blocking :meth:`wait`
            immediately; pass a callable to take over (tests).
        async_sleep: Override the async wait between polls. By default the engine
            races the delay against cancellation.
    """

    def __init__(
        self,
        *,
        interval: float = 5.0,
        timeout: float = 1800.0,
        on_progress: OperationCallback | None = None,
        transient_statuses: frozenset[int] = RETRYABLE_HTTP,
        jitter: float = 0.0,
        clock: Callable[[], float] = time.monotonic,
        sleep: Callable[[float], None] | None = None,
        async_sleep: Callable[[float], Awaitable[None]] | None = None,
    ) -> None:
        self._interval = interval
        self._timeout = timeout
        self._on_progress = on_progress
        self._transient = transient_statuses
        self._jitter = max(0.0, float(jitter))
        self._clock = clock
        self._sleep = sleep
        self._async_sleep = async_sleep
        self._status: OperationStatus | None = None
        self._cancelled = threading.Event()
        self._loop: asyncio.AbstractEventLoop | None = None
        self._async_cancelled: asyncio.Event | None = None

    # -- the lifecycle -----------------------------------------------------

    @property
    def last_status(self) -> OperationStatus | None:
        """The most recent snapshot, or ``None`` before the first poll."""
        return self._status

    @property
    def interval(self) -> float:
        """Seconds between polls when the attempt sends no ``Retry-After``."""
        return self._interval

    @property
    def timeout(self) -> float:
        """Maximum seconds to wait before raising :class:`OperationTimeoutError`."""
        return self._timeout

    def cancel(self) -> None:
        """Request cancellation of the long-running operation.

        Sends the service-side cancel request (:meth:`_send_cancel`, when the
        operation has one) and signals any in-flight :meth:`wait` — running in
        another thread — to stop at the next poll boundary, where it raises
        :class:`OperationCancelledError`. A later :meth:`wait` returns cancelled
        immediately.

        Cancellation is cooperative and **not** a rollback: work the service
        already applied remains. Without a cancel request this is client-side
        only and the service operation keeps running.
        """
        self._cancelled.set()
        self._wake_async_waiters()
        self._send_cancel()

    async def cancel_async(self) -> None:
        """Async twin of :meth:`cancel`."""
        self._cancelled.set()
        if self._async_cancelled is not None:
            self._async_cancelled.set()
        await self._send_cancel_async()

    def stream(
        self,
        *,
        timeout: float | None = None,
        on_progress: OperationCallback | None = None,
    ) -> Iterator[OperationStatus]:
        """Poll (blocking) and yield every :class:`OperationStatus` snapshot.

        The loop :meth:`wait` runs, exposed as an iterator: each poll yields its
        snapshot, the terminal one last. Nothing is raised for a failed or
        cancelled terminal status — the caller sees it and decides:

        ```python
        for status in operation.stream():
            print(status.status, status.percentage_complete)
        ```

        Args:
            timeout: Override the instance timeout for this call.
            on_progress: Override the instance progress callback.

        Raises:
            OperationTimeoutError: When the deadline elapses before a terminal state.
        """
        return self._snapshots(timeout=timeout, on_progress=on_progress)

    def wait(
        self,
        *,
        timeout: float | None = None,
        on_progress: OperationCallback | None = None,
        raise_on_failure: bool = True,
    ) -> T:
        """Poll (blocking) until the operation is terminal.

        The terminal snapshot of :meth:`stream`, with the failure policy applied
        and mapped through :meth:`_outcome`.

        Args:
            timeout: Override the instance timeout for this call.
            on_progress: Override the instance progress callback.
            raise_on_failure: Raise :class:`OperationFailedError` on a failed
                terminal status (default); pass ``False`` to return it instead.

        Returns:
            :meth:`_outcome` of the terminal :class:`OperationStatus`.
        """
        status: OperationStatus | None = None
        for snapshot in self.stream(timeout=timeout, on_progress=on_progress):
            status = snapshot
        assert status is not None  # the loop always yields at least one snapshot
        return self._outcome(self._finish(status, raise_on_failure))

    async def astream(
        self,
        *,
        timeout: float | None = None,
        on_progress: OperationCallback | None = None,
        cancel_on_task_cancel: bool = False,
    ) -> AsyncIterator[OperationStatus]:
        """Poll without blocking the loop, yielding every snapshot.

        Async twin of :meth:`stream`: ``async for status in operation.astream()``.
        The wait between polls yields to the event loop, so concurrently-running
        tasks keep making progress.
        """
        async for status in self._snapshots_async(
            timeout=timeout,
            on_progress=on_progress,
            cancel_on_task_cancel=cancel_on_task_cancel,
        ):
            yield status

    async def wait_async(
        self,
        *,
        timeout: float | None = None,
        on_progress: OperationCallback | None = None,
        raise_on_failure: bool = True,
        cancel_on_task_cancel: bool = False,
    ) -> T:
        """Await polling until the operation is terminal, without blocking the loop.

        Async twin of :meth:`wait`; the wait between polls yields to the event
        loop so concurrently-running tasks keep making progress.

        Args:
            cancel_on_task_cancel: When the surrounding task is cancelled, also
                request server-side cancellation (via :meth:`_send_cancel_async`)
                before the :class:`asyncio.CancelledError` propagates. Default
                ``False`` — cancelling the task stops *waiting* only; the service
                operation keeps running.
        """
        status: OperationStatus | None = None
        async for snapshot in self._snapshots_async(
            timeout=timeout,
            on_progress=on_progress,
            cancel_on_task_cancel=cancel_on_task_cancel,
        ):
            status = snapshot
        assert status is not None
        return self._outcome(self._finish(status, raise_on_failure))

    # -- what a subclass supplies ------------------------------------------

    def _step(self) -> OperationStatus:
        """Take one poll, blocking. A transient HTTP status means "try again"."""
        raise NotImplementedError

    async def _step_async(self) -> OperationStatus:
        """Async twin of :meth:`_step`."""
        raise NotImplementedError

    def _send_cancel(self) -> None:
        """Ask the service to cancel the operation, when it has a cancel request."""

    async def _send_cancel_async(self) -> None:
        """Async twin of :meth:`_send_cancel`."""

    def _observable(self, status: OperationStatus) -> bool:
        """Whether an attempt is worth reporting as a snapshot.

        Everything is reported by default: a monitor URL's ``429`` carries the
        service's own reason, so a progress hook should see it. A family whose
        transient status is a *gap* overrides this to ``False`` for it — an entity
        a service publishes a moment late answers ``404`` and has no status to
        show, so the wait retries without telling the progress hook that the
        operation did anything.
        """
        return True

    def _outcome(self, status: OperationStatus) -> T:
        """What :meth:`wait` returns for a terminal status — the snapshot by default."""
        return cast(T, status)

    # -- the polling loop --------------------------------------------------

    def _snapshots(
        self,
        *,
        timeout: float | None,
        on_progress: OperationCallback | None,
    ) -> Iterator[OperationStatus]:
        """Poll once per iteration and yield each snapshot until it is terminal."""
        effective_timeout = self._timeout if timeout is None else timeout
        deadline = self._clock() + effective_timeout
        while True:
            if self._cancelled.is_set():
                # Synthetic: the service has not reported anything, so the progress
                # callback is not told that it did.
                yield self._cancelled_status()
                return
            status = self._step()
            if not self._observed(status, on_progress):
                self._pause(status, deadline, effective_timeout)
                continue
            yield status
            if self._done(status):
                return
            self._pause(status, deadline, effective_timeout)

    async def _snapshots_async(
        self,
        *,
        timeout: float | None,
        on_progress: OperationCallback | None,
        cancel_on_task_cancel: bool = False,
    ) -> AsyncIterator[OperationStatus]:
        """Async twin of :meth:`_snapshots`."""
        effective_timeout = self._timeout if timeout is None else timeout
        deadline = self._clock() + effective_timeout
        self._async_cancelled = asyncio.Event()
        if self._cancelled.is_set():
            self._async_cancelled.set()
        self._loop = asyncio.get_running_loop()
        try:
            while True:
                if self._cancelled.is_set():
                    yield self._cancelled_status()
                    return
                status = await self._step_async()
                if not self._observed(status, on_progress):
                    await self._pause_async(status, deadline, effective_timeout)
                    continue
                yield status
                if self._done(status):
                    return
                await self._pause_async(status, deadline, effective_timeout)
        except asyncio.CancelledError:
            if cancel_on_task_cancel:
                try:
                    await asyncio.shield(self._send_cancel_async())
                except Exception:  # noqa: BLE001 - best effort; the cancellation must win
                    pass
            raise
        finally:
            self._loop = None
            self._async_cancelled = None

    # -- internals ---------------------------------------------------------

    def _observed(self, status: OperationStatus, on_progress: OperationCallback | None) -> bool:
        """Record ``status`` when it is an observation, and say whether to yield it."""
        if not self._observable(status):
            return False
        self._status = status
        callback = on_progress or self._on_progress
        if callable(callback):
            callback(status)
        return True

    def _done(self, status: OperationStatus) -> bool:
        """Whether this attempt ends the wait: terminal, and not merely "busy"."""
        return status.http_status not in self._transient and status.is_terminal

    @staticmethod
    def _cancelled_status() -> OperationStatus:
        """A synthetic terminal status for a client-requested cancellation."""
        return OperationStatus(status="cancelled")

    def _delay(self, status: OperationStatus) -> float:
        """Seconds to wait before the next poll (server ``Retry-After`` wins)."""
        if status.retry_after is not None:
            delay = float(status.retry_after)
        else:
            retry_after = response_retry_after(status.response) if status.response is not None else None
            delay = float(retry_after) if retry_after is not None else float(self._interval)
        return max(0.0, self._spread(delay))

    def _spread(self, delay: float) -> float:
        """Apply the jitter fraction, so simultaneous pollers do not stay in step."""
        if self._jitter <= 0 or delay <= 0:
            return delay
        return delay * (1.0 + random.uniform(-self._jitter, self._jitter))  # noqa: S311 - pacing, not crypto

    def _pause(self, status: OperationStatus, deadline: float, timeout: float) -> None:
        delay = self._delay(status)
        if self._clock() + delay > deadline:
            raise OperationTimeoutError(timeout)
        if self._sleep is not None:
            self._sleep(delay)
        else:
            # Wake immediately when cancel() is called (including from another thread).
            self._cancelled.wait(delay)

    async def _pause_async(self, status: OperationStatus, deadline: float, timeout: float) -> None:
        delay = self._delay(status)
        if self._clock() + delay > deadline:
            raise OperationTimeoutError(timeout)
        if self._async_sleep is not None:
            await self._async_sleep(delay)
            return
        event = self._async_cancelled
        if event is None or delay <= 0:
            await asyncio.sleep(max(0.0, delay))
            return
        try:
            # Race the delay against cancellation so a long Retry-After doesn't
            # delay a cancel; asyncio.wait_for cancels the pending wait on timeout.
            await asyncio.wait_for(event.wait(), timeout=delay)
        except asyncio.TimeoutError:
            pass

    def _wake_async_waiters(self) -> None:
        """Signal the async wait loop from any thread (thread-safe)."""
        event = self._async_cancelled
        loop = self._loop
        if event is None or loop is None or loop.is_closed():
            return
        try:
            loop.call_soon_threadsafe(event.set)
        except RuntimeError:  # loop closed between the check and the call
            pass

    @staticmethod
    def _finish(status: OperationStatus, raise_on_failure: bool) -> OperationStatus:
        if raise_on_failure:
            if status.is_cancelled:
                raise OperationCancelledError(status)
            if status.is_failure:
                raise OperationFailedError(status)
        return status
