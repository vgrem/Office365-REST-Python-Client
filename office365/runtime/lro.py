"""Long-running operations tracked by a monitor URL.

Microsoft Graph and several Microsoft 365 services model long-running work with
the async pattern described in
`Working with long-running actions <https://learn.microsoft.com/en-us/graph/long-running-actions-overview>`_:
the initial request is accepted with ``202 Accepted`` and a header pointing at an
*operation status* URL; the client polls that URL, honoring ``Retry-After``,
until the operation reaches a terminal status, then reads the result (often via
``resourceId`` / ``resourceLocation``).

This module is one of four families of the shared wait in
:mod:`office365.runtime.operation`: it says what *one poll* is for a monitor URL (a
``GET`` of that URL over the transport) and inherits the deadline, the pacing, the
cancel and the streaming from :class:`~office365.runtime.operation.Operation`::

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

The status vocabulary and the engine live in :mod:`office365.runtime.operation` and
are re-exported here, so ``from office365.runtime.lro import OperationStatus`` keeps
working.
"""

from __future__ import annotations

import time
from typing import TYPE_CHECKING, Any, AsyncIterator, Awaitable, Callable, Iterator

from requests import Response

from office365.runtime.client_request_exception import ClientRequestException
from office365.runtime.client_result import ClientResult
from office365.runtime.http.http_method import HttpMethod
from office365.runtime.http.request_options import RequestOptions
from office365.runtime.operation import (
    CANCELLED_STATUSES,
    FAILURE_STATUSES,
    PARTIAL_STATUSES,
    POLL_URL_HEADERS,
    RETRYABLE_HTTP,
    SUCCESS_STATUSES,
    ContinuationToken,
    Operation,
    OperationCallback,
    OperationCancelledError,
    OperationError,
    OperationFailedError,
    OperationStatus,
    OperationTimeoutError,
    resolve_poll_url,
)

if TYPE_CHECKING:
    from office365.runtime.client_runtime_context import ClientRuntimeContext
    from office365.runtime.transport.base import BaseTransport

__all__ = [
    "CANCELLED_STATUSES",
    "FAILURE_STATUSES",
    "PARTIAL_STATUSES",
    "POLL_URL_HEADERS",
    "RETRYABLE_HTTP",
    "SUCCESS_STATUSES",
    "ContinuationToken",
    "LongRunningOperationResult",
    "Operation",
    "OperationCallback",
    "OperationCancelledError",
    "OperationError",
    "OperationFailedError",
    "OperationPoller",
    "OperationStatus",
    "OperationTimeoutError",
    "resolve_poll_url",
]


class OperationPoller(Operation[OperationStatus]):
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
        super().__init__(
            interval=interval,
            timeout=timeout,
            on_progress=on_progress,
            clock=clock,
            sleep=sleep,
            async_sleep=async_sleep,
        )
        self._context = context
        self._poll_url = poll_url
        self._final_state_via = final_state_via
        self._authenticate = authenticate
        self._cancel_request = cancel_request
        self._transport = transport
        self._async_transport = async_transport

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

    def to_continuation_token(self) -> ContinuationToken:
        """Snapshot the poller so the operation can be resumed later."""
        return ContinuationToken(
            poll_url=self._poll_url,
            final_state_via=self._final_state_via,
            status=self.last_status.status if self.last_status is not None else None,
        )

    # -- one poll ----------------------------------------------------------

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

    def _step(self) -> OperationStatus:
        client_request = self._context.pending_request()
        transport = self._transport or client_request.transport
        request = self._build_request()
        if self._authenticate:
            client_request.beforeExecute(request)
        client_request.apply_client_request_id(request)
        return self._to_status(transport.execute(request))

    async def _step_async(self) -> OperationStatus:
        client_request = self._context.pending_request()
        transport = self._async_transport or client_request.async_transport
        request = self._build_request()
        if self._authenticate:
            await client_request.before_execute_async(request)
        client_request.apply_client_request_id(request)
        return self._to_status(await transport.execute_async(request))

    @staticmethod
    def _to_status(response: Response) -> OperationStatus:
        """Classify a poll response, raising for permanent HTTP failures."""
        status = OperationStatus.from_response(response)
        if status.http_status not in RETRYABLE_HTTP and status.http_status >= 400:  # noqa: PLR2004
            raise ClientRequestException.from_response(response)
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

    The same type describes work that finished in the submitting round-trip
    (:meth:`completed`): it has no monitor URL, and ``wait()`` answers the status
    it was given without a request, so a caller that opted into the async pattern
    does not have to branch on which way the service answered.
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

    @classmethod
    def completed(
        cls,
        context: "ClientRuntimeContext",
        response: Response,
        *,
        authenticate: bool = False,
        final_state_via: str = "auto",
    ) -> "LongRunningOperationResult":
        """Describe work the service finished in the submitting round-trip.

        ``Prefer: respond-async`` is a *preference*: a quick call is answered
        normally. That answer is already the outcome, so the result is born
        terminal — ``wait()`` returns its status without polling, and the query
        holds the payload. ``status`` is reported as ``"completed"`` because the
        round-trip that started the work also ended it.

        Args:
            context: The client runtime context that owns the credentials.
            response: The synchronous response the query was fed with.
        """
        result = cls(context, None, authenticate=authenticate, final_state_via=final_state_via)
        result._last_status = OperationStatus(
            status="completed",
            http_status=int(getattr(response, "status_code", 0) or 0),
            response=response,
        )
        return result

    @property
    def monitor_url(self) -> str | None:
        """The operation-status URL, or ``None`` when the work completed in one round-trip."""
        return self.value or None

    @property
    def last_status(self) -> OperationStatus | None:
        """The most recent snapshot.

        ``None`` before the first poll; already the terminal snapshot for an
        operation that :meth:`completed` synchronously.
        """
        return self._last_status

    @property
    def is_completed(self) -> bool:
        """Whether a terminal snapshot is already known (no poll needed)."""
        return self._settled() is not None

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

    def _settled(self) -> OperationStatus | None:
        """The terminal snapshot already known, if waiting again would change nothing.

        A synchronously completed operation has one from birth; a polled one keeps
        the one ``wait()`` returned. A terminal *failure* is deliberately not
        cached-and-replayed: re-waiting a failed operation retries the poll (and
        raises again), which is what a caller looping on ``wait()`` expects.
        """
        status = self._last_status
        if status is not None and status.is_terminal and not status.is_failure:
            return status
        return None

    def wait(
        self,
        *,
        interval: float = 5.0,
        timeout: float = 1800.0,
        on_progress: OperationCallback | None = None,
        raise_on_failure: bool = True,
    ) -> OperationStatus:
        """Poll (blocking) until the operation is terminal and return the status."""
        settled = self._settled()
        if settled is not None:
            return settled
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
        settled = self._settled()
        if settled is not None:
            return settled
        poller = self.to_poller(interval=interval, timeout=timeout, on_progress=on_progress)
        self._poller = poller
        self._last_status = await poller.wait_async(on_progress=on_progress, raise_on_failure=raise_on_failure)
        return self._last_status

    def stream(
        self,
        *,
        interval: float = 5.0,
        timeout: float = 1800.0,
        on_progress: OperationCallback | None = None,
    ) -> Iterator[OperationStatus]:
        """Poll and yield every status snapshot until the operation is terminal."""
        settled = self._settled()
        if settled is not None:
            return iter((settled,))
        poller = self.to_poller(interval=interval, timeout=timeout, on_progress=on_progress)
        self._poller = poller
        return self._track(poller.stream(on_progress=on_progress))

    def astream(
        self,
        *,
        interval: float = 5.0,
        timeout: float = 1800.0,
        on_progress: OperationCallback | None = None,
    ) -> AsyncIterator[OperationStatus]:
        """Await polling and yield every snapshot (async twin of :meth:`stream`)."""
        settled = self._settled()
        if settled is not None:
            return self._only(settled)
        poller = self.to_poller(interval=interval, timeout=timeout, on_progress=on_progress)
        self._poller = poller
        return self._track_async(poller.astream(on_progress=on_progress))

    async def _only(self, status: OperationStatus) -> AsyncIterator[OperationStatus]:
        """An async stream of a single, already-known snapshot."""
        yield status

    def _track(self, snapshots: Iterator[OperationStatus]) -> Iterator[OperationStatus]:
        """Keep :attr:`last_status` current while the caller consumes a stream."""
        for status in snapshots:
            self._last_status = status
            yield status

    async def _track_async(self, snapshots: AsyncIterator[OperationStatus]) -> AsyncIterator[OperationStatus]:
        """Async twin of :meth:`_track`."""
        async for status in snapshots:
            self._last_status = status
            yield status

    def cancel(self) -> None:
        """Request cancellation of the tracked operation.

        Cancels the poller used by the most recent :meth:`wait` / :meth:`wait_async`
        (or :meth:`stream` / :meth:`astream`) call, so an in-flight wait stops at
        the next poll boundary. See :meth:`OperationPoller.cancel` for the full
        semantics.
        """
        if self._poller is not None:
            self._poller.cancel()
