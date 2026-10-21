"""Waitable long-running-operation entities.

Not every long-running operation is tracked by a bare monitor URL: Microsoft
Graph also exposes *operation entities* — ordinary resources whose ``status``
property describes the progress of the work (``RichLongRunningOperation``,
``WorkbookOperation``, ``TelephoneNumberLongRunningOperation``, ``TeamsAsyncOperation``
and friends). This module adds a small :class:`PollableOperation` mixin so those
entities can be awaited directly::

    operation = client.sites.get_by_id(site_id).operations[...]
    operation.get().execute_query()
    await operation.wait_async()  # re-fetches until the status is terminal

The mixin re-issues a plain ``GET`` for the entity (through the normal request
pipeline, so auth and the sync/async split all apply), honors the server's
``Retry-After`` between polls, and treats a transient ``404`` as a "not created
yet" gap — matching the behaviour Microsoft documents for async operations that
are briefly unavailable right after creation.
"""

from __future__ import annotations

import asyncio
import time
from enum import Enum
from typing import TYPE_CHECKING, Any, Callable, cast

from requests import Response
from typing_extensions import Self

from office365.runtime.client_request_exception import ClientRequestException
from office365.runtime.lro import (
    OperationFailedError,
    OperationStatus,
    OperationTimeoutError,
)
from office365.runtime.queries.read_entity import ReadEntityQuery
from office365.runtime.retry import response_retry_after

if TYPE_CHECKING:
    from office365.runtime.client_object import ClientObject

#: HTTP statuses that merely mean "poll again later" while waiting on an entity.
TRANSIENT_POLL_STATUSES = frozenset({404, 429, 503})


def normalize_status(value: Any) -> str | None:
    """Return a comparable, lower-cased status for a string or enum value."""
    if value is None:
        return None
    if isinstance(value, Enum):
        value = value.name
    return str(value).strip().lower()


def is_transient_poll_error(ex: Exception) -> bool:
    """Whether ``ex`` is a retryable poll failure (e.g. a ``404`` gap)."""
    status = getattr(getattr(ex, "response", None), "status_code", None)
    return status in TRANSIENT_POLL_STATUSES


def next_poll_delay(response: Response | None, interval: float) -> float:
    """Seconds until the next poll: the server's ``Retry-After`` wins over ``interval``."""
    retry_after = response_retry_after(response) if response is not None else None
    if retry_after is not None:
        return max(0.0, float(retry_after))
    return max(0.0, float(interval))


def reload_operation(operation: "ClientObject") -> Response:
    """GET an operation entity and return the raw response, refreshing it in place.

    Executes the ``GET`` through the request pipeline (so ``beforeExecute`` hooks
    such as auth run) but skips the context queue, returning the response so the
    caller can read ``Retry-After``.
    """
    query = ReadEntityQuery(operation)
    request = operation.context.pending_request()
    request_options = request.build_request(query)
    with operation.context.current_query_scope(query):
        response = request.execute_request_direct(request_options)
        request.handle_response(response, query)
    return response


async def reload_operation_async(operation: "ClientObject") -> Response:
    """Async twin of :func:`reload_operation`."""
    query = ReadEntityQuery(operation)
    request = operation.context.pending_request()
    request_options = request.build_request(query)
    with operation.context.current_query_scope(query):
        response = await request.execute_request_direct_async(request_options)
        request.handle_response(response, query)
    return response


class PollableOperation:
    """Mixin that makes an entity with a ``status`` property awaitable.

    Host classes (``ClientObject`` subclasses) provide the entity fields; the
    mixin adds :meth:`wait` / :meth:`wait_async` plus the
    :attr:`is_operation_complete` / :attr:`is_operation_failed` helpers.
    """

    #: Seconds between polls when the server sends no ``Retry-After``.
    operation_polling_interval: float = 10.0

    #: Maximum seconds to wait before raising :class:`OperationTimeoutError`.
    operation_polling_timeout: float = 1800.0

    @property
    def operation_status(self) -> str | None:
        """The raw ``status`` value, or ``None`` when the response has no ``status``."""
        value = cast("ClientObject", self).properties.get("status")
        return value.name if isinstance(value, Enum) else value

    @property
    def is_operation_complete(self) -> bool:
        """Whether the last-seen status is terminal (succeeded *or* failed)."""
        return self._operation_snapshot().is_terminal

    @property
    def is_operation_failed(self) -> bool:
        """Whether the last-seen status is a failed terminal status."""
        return self._operation_snapshot().is_failure

    def wait(
        self,
        *,
        timeout: float | None = None,
        interval: float | None = None,
        on_progress: Callable[[OperationStatus], None] | None = None,
        raise_on_failure: bool = True,
        clock: Callable[[], float] = time.monotonic,
        sleep: Callable[[float], None] = time.sleep,
    ) -> Self:
        """Re-fetch (blocking) until the operation is terminal.

        Args:
            timeout: Maximum seconds to wait (defaults to
                :attr:`operation_polling_timeout`).
            interval: Seconds between polls when no ``Retry-After`` is sent
                (defaults to :attr:`operation_polling_interval`).
            on_progress: Called with each :class:`OperationStatus` snapshot.
            raise_on_failure: Raise :class:`OperationFailedError` on a failed
                terminal status (default); pass ``False`` to return ``self``.
            clock: Injectable monotonic clock (tests).
            sleep: Injectable synchronous sleep (tests).

        Returns:
            ``self``, refreshed to its terminal state.

        Raises:
            OperationFailedError: On a failed terminal status (unless disabled).
            OperationTimeoutError: When the deadline elapses first.
        """
        operation = cast("ClientObject", self)
        interval = self.operation_polling_interval if interval is None else interval
        effective_timeout = self.operation_polling_timeout if timeout is None else timeout
        deadline = clock() + effective_timeout
        while True:
            try:
                response = reload_operation(operation)
            except ClientRequestException as ex:
                if not is_transient_poll_error(ex):
                    raise
                if clock() >= deadline:
                    raise OperationTimeoutError(effective_timeout) from ex
                sleep(next_poll_delay(ex.response, interval))
                continue
            snapshot = self._operation_snapshot(response)
            if callable(on_progress):
                on_progress(snapshot)
            if snapshot.is_terminal:
                if raise_on_failure and snapshot.is_failure:
                    raise OperationFailedError(snapshot)
                return self
            if clock() >= deadline:
                raise OperationTimeoutError(effective_timeout)
            sleep(next_poll_delay(response, interval))

    async def wait_async(
        self,
        *,
        timeout: float | None = None,
        interval: float | None = None,
        on_progress: Callable[[OperationStatus], None] | None = None,
        raise_on_failure: bool = True,
        clock: Callable[[], float] = time.monotonic,
        async_sleep: Callable[[float], Any] = asyncio.sleep,
    ) -> Self:
        """Await the operation until it is terminal, without blocking the loop.

        Async twin of :meth:`wait`; the delay between polls yields to the event
        loop so concurrently-running tasks keep making progress.
        """
        operation = cast("ClientObject", self)
        interval = self.operation_polling_interval if interval is None else interval
        effective_timeout = self.operation_polling_timeout if timeout is None else timeout
        deadline = clock() + effective_timeout
        while True:
            try:
                response = await reload_operation_async(operation)
            except ClientRequestException as ex:
                if not is_transient_poll_error(ex):
                    raise
                if clock() >= deadline:
                    raise OperationTimeoutError(effective_timeout) from ex
                await async_sleep(next_poll_delay(ex.response, interval))
                continue
            snapshot = self._operation_snapshot(response)
            if callable(on_progress):
                on_progress(snapshot)
            if snapshot.is_terminal:
                if raise_on_failure and snapshot.is_failure:
                    raise OperationFailedError(snapshot)
                return self
            if clock() >= deadline:
                raise OperationTimeoutError(effective_timeout)
            await async_sleep(next_poll_delay(response, interval))

    # -- internals ---------------------------------------------------------

    def _operation_snapshot(self, response: Response | None = None) -> OperationStatus:
        """Build a snapshot from the refreshed entity (falling back to its properties)."""
        properties = cast("ClientObject", self).properties
        snapshot = OperationStatus.from_response(response) if response is not None else OperationStatus()
        if snapshot.status is None:
            snapshot.status = self.operation_status
        if snapshot.resource_id is None:
            snapshot.resource_id = properties.get("resourceId")
        if snapshot.resource_location is None:
            snapshot.resource_location = properties.get("resourceLocation") or properties.get("targetResourceLocation")
        return snapshot
