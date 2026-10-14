"""First-class polling for long-running operations (LRO).

Microsoft Graph and several Microsoft 365 services model long-running work with
the async pattern described in
`Working with long-running actions <https://learn.microsoft.com/en-us/graph/long-running-actions-overview>`_:
the initial request is accepted with ``202 Accepted`` and a header pointing at an
*operation status* URL; the client polls that URL, honoring ``Retry-After``,
until the operation reaches a terminal status, then reads the result (often via
``resourceId`` / ``resourceLocation``).

This module provides a transport-agnostic poller usable from both the
synchronous and asynchronous APIs::

    op = OperationPoller.from_response(context, response)
    status = op.wait()  # blocking
    status = await op.wait_async()  # non-blocking

The design mirrors ``azure-core``'s ``LROPoller`` / ``AsyncLROPoller``: pluggable
poll-URL resolution (``Operation-Location`` / ``Azure-AsyncOperation`` /
``Location``), ``Retry-After``-driven pacing, terminal-state detection, an
optional progress hook, and continuation tokens so a long job can be resumed in
a later call or process.

The monitor URL returned by Microsoft Graph is short-lived, unique to the
original caller and **does not require authentication**; it can even live on a
different host (e.g. ``api.onedrive.com``). The poller therefore does not attach
credentials by default — pass ``authenticate=True`` for services such as Azure
that do require them.

An in-flight wait can be cancelled cooperatively with
:meth:`OperationPoller.cancel` (or :meth:`OperationPoller.cancel_async`).
"""

from __future__ import annotations

import asyncio
import json
import threading
import time
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Awaitable, Callable

from requests import Response

from office365.runtime.client_request_exception import ClientRequestException
from office365.runtime.client_result import ClientResult
from office365.runtime.http.http_method import HttpMethod
from office365.runtime.http.request_options import RequestOptions
from office365.runtime.retry import response_retry_after

if TYPE_CHECKING:
    from office365.runtime.client_request import ClientRequest
    from office365.runtime.client_runtime_context import ClientRuntimeContext
    from office365.runtime.transport.base import BaseTransport

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

_PENDING_HTTP = 202

#: HTTP statuses that ask the client to back off and poll again (throttling).
_RETRYABLE_HTTP = frozenset({429, 503})

#: Callback invoked with the latest :class:`OperationStatus` on every poll.
OperationCallback = Callable[["OperationStatus"], None]


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
        error: Error payload when the operation failed.
        response: The raw terminal/poll response (carries the result body, e.g. a
            report export), excluded from ``repr``.
    """

    status: str | None = None
    http_status: int = 0
    percentage_complete: float | None = None
    resource_id: str | None = None
    resource_location: str | None = None
    error: Any = None
    response: Response | None = field(default=None, repr=False)

    @classmethod
    def from_response(cls, response: Response) -> "OperationStatus":
        """Build a snapshot from a poll response."""
        data = _parse_json(response)
        return cls(
            status=_first(data, "status", "operationStatus"),
            http_status=int(getattr(response, "status_code", 0) or 0),
            percentage_complete=_percentage(data),
            resource_id=_first(data, "resourceId"),
            resource_location=_first(data, "resourceLocation", "targetResourceLocation"),
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
            return key in SUCCESS_STATUSES or key in FAILURE_STATUSES
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
    """Raised when an operation does not finish before the timeout."""

    def __init__(self, timeout: float) -> None:
        self.timeout = timeout
        super().__init__(f"Timed out after {timeout}s waiting for the long-running operation")


class OperationPoller:
    """Polls a long-running-operation monitor URL until it reaches a terminal state.

    Build it from the initial ``202`` response (:meth:`from_response`), a known
    monitor URL, or a resumed :class:`ContinuationToken`
    (:meth:`from_continuation_token`), then block with :meth:`wait` or await
    :meth:`wait_async`.

    Args:
        context: The client context whose request/transport is used to poll.
        poll_url: Absolute operation-status URL (may be cross-host).
        final_state_via: How the poll URL was selected (kept for continuation).
        interval: Seconds between polls when the server sends no ``Retry-After``.
        timeout: Maximum seconds to wait before raising
            :class:`OperationTimeoutError` (default 30 minutes).
        authenticate: Attach the context's credentials to each poll. Default
            ``False`` — Graph monitor URLs are unauthenticated and may be on a
            different host.
        on_progress: Optional default callback invoked with each
            :class:`OperationStatus` snapshot.
        cancel_request: Optional request that cancels the operation server-side,
            sent by :meth:`cancel` / :meth:`cancel_async` (service-specific, e.g.
            a ``DELETE`` on a Graph operation resource).
        transport: Override the synchronous transport used by :meth:`wait`.
        async_transport: Override the transport used by :meth:`wait_async`.
        clock: Injectable monotonic clock (tests).
        sleep: Override the wait between polls. By default the poller waits on
            an internal event, so :meth:`cancel` wakes a blocking :meth:`wait`
            immediately; pass a callable to take over the waiting (tests).
        async_sleep: Override the async wait between polls. By default the
            poller races the delay against cancellation, so :meth:`cancel` /
            :meth:`cancel_async` wake :meth:`wait_async` immediately.
    """

    def __init__(
        self,
        context: "ClientRuntimeContext",
        poll_url: str,
        *,
        final_state_via: str = "auto",
        interval: float = 5.0,
        timeout: float = 1800.0,
        authenticate: bool = False,
        on_progress: OperationCallback | None = None,
        cancel_request: "RequestOptions | None" = None,
        transport: "BaseTransport | None" = None,
        async_transport: "BaseTransport | None" = None,
        clock: Callable[[], float] = time.monotonic,
        sleep: Callable[[float], None] | None = None,
        async_sleep: Callable[[float], Awaitable[None]] | None = None,
    ) -> None:
        self._context = context
        self._poll_url = poll_url
        self._final_state_via = final_state_via
        self._interval = interval
        self._timeout = timeout
        self._authenticate = authenticate
        self._on_progress = on_progress
        self._cancel_request = cancel_request
        self._transport = transport
        self._async_transport = async_transport
        self._clock = clock
        self._sleep = sleep
        self._async_sleep = async_sleep
        self._status: OperationStatus | None = None
        self._cancelled = threading.Event()
        self._loop: asyncio.AbstractEventLoop | None = None
        self._async_cancelled: asyncio.Event | None = None

    @classmethod
    def from_response(
        cls,
        context: "ClientRuntimeContext",
        response: Response,
        *,
        final_state_via: str = "auto",
        original_url: str | None = None,
        **options: Any,
    ) -> "OperationPoller":
        """Create a poller from a ``202 Accepted`` response.

        Raises:
            ValueError: When no monitor URL header is present (the response is
                not an accepted long-running operation).
        """
        poll_url = resolve_poll_url(response, final_state_via=final_state_via, original_url=original_url)
        if poll_url is None:
            raise ValueError(
                "No long-running-operation monitor URL found (looked for "
                f"{', '.join(POLL_URL_HEADERS)}); the response is not an accepted async operation."
            )
        return cls(context, poll_url, final_state_via=final_state_via, **options)

    @classmethod
    def from_continuation_token(
        cls,
        context: "ClientRuntimeContext",
        token: ContinuationToken | str | bytes | dict[str, Any],
        **options: Any,
    ) -> "OperationPoller":
        """Resume a poller from a previously emitted :class:`ContinuationToken`."""
        if isinstance(token, (str, bytes)):
            token = ContinuationToken.from_json(token)
        elif isinstance(token, dict):
            token = ContinuationToken.from_json(token)
        options.setdefault("final_state_via", token.final_state_via)
        return cls(context, token.poll_url, **options)

    @property
    def poll_url(self) -> str:
        """The operation-status URL being polled."""
        return self._poll_url

    @property
    def final_state_via(self) -> str:
        """How the poll URL was selected (``auto`` / ``location`` / ...)."""
        return self._final_state_via

    @property
    def last_status(self) -> OperationStatus | None:
        """The most recent snapshot, or ``None`` before the first poll."""
        return self._status

    def to_continuation_token(self) -> ContinuationToken:
        """Snapshot the poller so the operation can be resumed later."""
        return ContinuationToken(
            poll_url=self._poll_url,
            final_state_via=self._final_state_via,
            status=self._status.status if self._status is not None else None,
        )

    def cancel(self) -> None:
        """Request cancellation of the long-running operation.

        Sends the configured service-side cancel request (``cancel_request``) and
        signals any in-flight :meth:`wait` — running in another thread — to stop
        at the next poll boundary, where it raises
        :class:`OperationCancelledError`. A later :meth:`wait` returns cancelled
        immediately.

        Cancellation is cooperative and **not** a rollback: work the service
        already applied remains. Without a ``cancel_request`` this is
        client-side only and the service operation keeps running.

        A blocking :meth:`wait` is woken immediately, even from another thread;
        a running :meth:`wait_async` is woken on its event loop.
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

    def wait(
        self,
        *,
        timeout: float | None = None,
        on_progress: OperationCallback | None = None,
        raise_on_failure: bool = True,
    ) -> OperationStatus:
        """Poll (blocking) until the operation is terminal.

        Args:
            timeout: Override the instance timeout for this call.
            on_progress: Override the instance progress callback.
            raise_on_failure: Raise :class:`OperationFailedError` on a failed
                terminal status (default); pass ``False`` to return it instead.

        Returns:
            The terminal :class:`OperationStatus`.
        """
        client_request = self._context.pending_request()
        transport = self._transport or client_request.transport
        effective_timeout = self._timeout if timeout is None else timeout
        deadline = self._clock() + effective_timeout
        while True:
            if self._cancelled.is_set():
                return self._finish(self._cancelled_status(), raise_on_failure)
            status = self._poll_sync(client_request, transport)
            self._record(status, on_progress)
            if status.http_status not in _RETRYABLE_HTTP and status.is_terminal:
                return self._finish(status, raise_on_failure)
            self._pause(status, deadline, effective_timeout)

    async def wait_async(
        self,
        *,
        timeout: float | None = None,
        on_progress: OperationCallback | None = None,
        raise_on_failure: bool = True,
        cancel_on_task_cancel: bool = False,
    ) -> OperationStatus:
        """Await polling until the operation is terminal, without blocking the loop.

        Async twin of :meth:`wait`; the wait between polls yields to the event
        loop so concurrently-running tasks keep making progress.

        Args:
            cancel_on_task_cancel: When the surrounding task is cancelled, also
                request server-side cancellation (via ``cancel_request``) before
                the :class:`asyncio.CancelledError` propagates. Default ``False``
                — cancelling the task stops *waiting* only; the service operation
                keeps running.
        """
        client_request = self._context.pending_request()
        transport = self._async_transport or client_request.async_transport
        effective_timeout = self._timeout if timeout is None else timeout
        deadline = self._clock() + effective_timeout
        self._async_cancelled = asyncio.Event()
        if self._cancelled.is_set():
            self._async_cancelled.set()
        self._loop = asyncio.get_running_loop()
        try:
            while True:
                if self._cancelled.is_set():
                    return self._finish(self._cancelled_status(), raise_on_failure)
                status = await self._poll_async(client_request, transport)
                self._record(status, on_progress)
                if status.http_status not in _RETRYABLE_HTTP and status.is_terminal:
                    return self._finish(status, raise_on_failure)
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

    @staticmethod
    def _cancelled_status() -> OperationStatus:
        """A synthetic terminal status for a client-requested cancellation."""
        return OperationStatus(status="cancelled")

    def _send_cancel(self) -> None:
        """Send the service-side cancel request, when one was configured."""
        if self._cancel_request is None:
            return
        client_request = self._context.pending_request()
        transport = self._transport or client_request.transport
        if self._authenticate:
            client_request.beforeExecute(self._cancel_request)
        transport.execute(self._cancel_request)

    async def _send_cancel_async(self) -> None:
        """Async twin of :meth:`_send_cancel`."""
        if self._cancel_request is None:
            return
        client_request = self._context.pending_request()
        transport = self._async_transport or client_request.async_transport
        if self._authenticate:
            await client_request.before_execute_async(self._cancel_request)
        await transport.execute_async(self._cancel_request)

    def _build_request(self) -> RequestOptions:
        return RequestOptions(url=self._poll_url, method=HttpMethod.Get)

    def _poll_sync(self, client_request: "ClientRequest", transport: "BaseTransport") -> OperationStatus:
        request = self._build_request()
        if self._authenticate:
            client_request.beforeExecute(request)
        client_request.apply_client_request_id(request)
        return self._to_status(transport.execute(request))

    async def _poll_async(self, client_request: "ClientRequest", transport: "BaseTransport") -> OperationStatus:
        request = self._build_request()
        if self._authenticate:
            await client_request.before_execute_async(request)
        client_request.apply_client_request_id(request)
        return self._to_status(await transport.execute_async(request))

    @staticmethod
    def _to_status(response: Response) -> OperationStatus:
        """Classify a poll response, raising for permanent HTTP failures."""
        status = OperationStatus.from_response(response)
        if status.http_status not in _RETRYABLE_HTTP and status.http_status >= 400:  # noqa: PLR2004
            raise ClientRequestException.from_response(response)
        return status

    def _record(self, status: OperationStatus, on_progress: OperationCallback | None) -> None:
        self._status = status
        callback = on_progress or self._on_progress
        if callable(callback):
            callback(status)

    def _delay(self, status: OperationStatus) -> float:
        """Seconds to wait before the next poll (server ``Retry-After`` wins)."""
        retry_after = response_retry_after(status.response) if status.response is not None else None
        if retry_after is not None:
            return float(retry_after)
        return max(0.0, float(self._interval))

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

    @staticmethod
    def _finish(status: OperationStatus, raise_on_failure: bool) -> OperationStatus:
        if raise_on_failure:
            if status.is_cancelled:
                raise OperationCancelledError(status)
            if status.is_failure:
                raise OperationFailedError(status)
        return status


class LongRunningOperationResult(ClientResult[str]):
    """A long-running operation accepted by the service and tracked by a monitor URL.

    Returned by actions such as Microsoft Graph ``driveItem.copy``: after
    ``execute_query()`` the result value holds the monitor URL from the
    ``Location`` header, and :meth:`wait` / :meth:`wait_async` poll it to
    completion::

        result = source_item.copy(name="report (copy).xlsx", parent=dest).execute_query()
        status = result.wait()  # or: status = await result.wait_async()

    Microsoft Graph hands back monitor URLs on the drive's host (OneDrive /
    SharePoint) that are pre-authenticated for the original caller, so by default
    no credentials are attached when polling — pass ``authenticate=True`` only for
    services (e.g. Azure) that require them.
    """

    def __init__(
        self,
        context: "ClientRuntimeContext",
        default_value: str | None = None,
        *,
        authenticate: bool = False,
        final_state_via: str = "auto",
    ) -> None:
        super().__init__(context, str() if default_value is None else default_value)
        self._authenticate = authenticate
        self._final_state_via = final_state_via
        self._last_status: OperationStatus | None = None
        self._poller: OperationPoller | None = None

    @property
    def monitor_url(self) -> str:
        """The operation-status URL (the result value)."""
        return self.value

    @property
    def last_status(self) -> OperationStatus | None:
        """The most recent snapshot, or ``None`` before the first poll."""
        return self._last_status

    @property
    def resource_id(self) -> str | None:
        """Identifier of the resource produced by the last poll, when reported."""
        return self._last_status.resource_id if self._last_status is not None else None

    @property
    def resource_location(self) -> str | None:
        """URL of the resource produced by the last poll, when reported."""
        return self._last_status.resource_location if self._last_status is not None else None

    def to_poller(
        self,
        *,
        interval: float = 5.0,
        timeout: float = 1800.0,
        on_progress: OperationCallback | None = None,
    ) -> OperationPoller:
        """Build a poller for this operation's monitor URL."""
        if not self.value:
            raise ValueError("The operation has no monitor URL yet — run execute_query() before wait().")
        return OperationPoller(
            self._context,
            self.value,
            final_state_via=self._final_state_via,
            interval=interval,
            timeout=timeout,
            authenticate=self._authenticate,
            on_progress=on_progress,
        )

    def wait(
        self,
        *,
        interval: float = 5.0,
        timeout: float = 1800.0,
        on_progress: OperationCallback | None = None,
        raise_on_failure: bool = True,
    ) -> OperationStatus:
        """Poll (blocking) until the operation is terminal and return the status."""
        poller = self.to_poller(interval=interval, timeout=timeout, on_progress=on_progress)
        self._poller = poller
        self._last_status = poller.wait(on_progress=on_progress, raise_on_failure=raise_on_failure)
        return self._last_status

    async def wait_async(
        self,
        *,
        interval: float = 5.0,
        timeout: float = 1800.0,
        on_progress: OperationCallback | None = None,
        raise_on_failure: bool = True,
    ) -> OperationStatus:
        """Await the operation to completion and return the terminal status."""
        poller = self.to_poller(interval=interval, timeout=timeout, on_progress=on_progress)
        self._poller = poller
        self._last_status = await poller.wait_async(on_progress=on_progress, raise_on_failure=raise_on_failure)
        return self._last_status

    def cancel(self) -> None:
        """Request cancellation of the tracked operation.

        Cancels the poller used by the most recent :meth:`wait` / :meth:`wait_async`
        call, so an in-flight wait stops at the next poll boundary. See
        :meth:`OperationPoller.cancel` for the full semantics.
        """
        if self._poller is not None:
            self._poller.cancel()
