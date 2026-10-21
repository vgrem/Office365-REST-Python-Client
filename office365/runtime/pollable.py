"""Waitable long-running-operation entities.

Not every long-running operation is tracked by a bare monitor URL: Microsoft
Graph also exposes *operation entities* — ordinary resources whose ``status``
property describes the progress of the work (``RichLongRunningOperation``,
``WorkbookOperation``, ``TelephoneNumberLongRunningOperation``,
``TeamsAsyncOperation`` and friends). This module adds a small
:class:`PollableOperation` mixin so those entities can be awaited directly::

    operation = client.sites.get_by_id(site_id).operations[...]
    operation.get().execute_query()
    await operation.wait_async()  # re-fetches until the status is terminal

One poll is a plain ``GET`` for the entity (through the normal request pipeline,
so auth and the sync/async split all apply); everything else — the deadline,
``Retry-After`` pacing, the progress hook, the cancel, and the stream — is the
shared wait in :mod:`office365.runtime.operation`. So this family is
:class:`Operation` specialised twice over:

- one attempt re-reads the entity, and a transient ``404`` is a "not created
  yet" gap — matching what Microsoft documents for async operations that are
  briefly unavailable right after creation — so it means "poll again" rather
  than "no such operation";
- a gap is an *attempt*, not an observation: the entity has no status to show,
  so ``on_progress`` is not told that anything happened (a monitor URL's
  ``429``, by contrast, carries the service's own reason and is reported);
- ``wait()`` returns the entity itself, refreshed to its terminal state, and
  ``stream()`` yields the snapshots, so a UI can follow the percentage without
  giving up the entity.
"""

from __future__ import annotations

import time
from enum import Enum
from typing import TYPE_CHECKING, Any, AsyncIterator, Callable, Iterator, cast

from requests import Response
from typing_extensions import Self

from office365.runtime.client_request_exception import ClientRequestException
from office365.runtime.lro import (
    OperationFailedError,
    OperationStatus,
    OperationTimeoutError,
)
from office365.runtime.operation import Operation
from office365.runtime.queries.read_entity import ReadEntityQuery
from office365.runtime.retry import response_retry_after

if TYPE_CHECKING:
    from office365.runtime.client_object import ClientObject

__all__ = [
    "TRANSIENT_POLL_STATUSES",
    "OperationFailedError",
    "OperationStatus",
    "OperationTimeoutError",
    "PollableOperation",
    "is_transient_poll_error",
    "next_poll_delay",
    "normalize_status",
    "reload_operation",
    "reload_operation_async",
]

#: HTTP statuses that merely mean "poll again later" while waiting on an entity.
#:
#: ``404`` because an operation entity may not be published the instant its
#: parent answers ``202``; ``429``/``503`` because the service is busy.
TRANSIENT_POLL_STATUSES = frozenset({404, 429, 503})

#: Transient statuses whose answer observes nothing about the operation.
_GAP_STATUSES = frozenset({404})


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


def operation_snapshot(entity: "ClientObject", response: Response | None = None) -> OperationStatus:
    """Build a snapshot from a refreshed entity (falling back to its properties).

    The entity's own ``status`` is the authority when the payload carries none —
    some services answer ``200`` with the entity and nothing else.
    """
    properties = entity.properties
    snapshot = OperationStatus.from_response(response) if response is not None else OperationStatus()
    if snapshot.status is None:
        value = properties.get("status")
        snapshot.status = value.name if isinstance(value, Enum) else value
    if snapshot.resource_id is None:
        snapshot.resource_id = properties.get("resourceId")
    if snapshot.resource_location is None:
        snapshot.resource_location = properties.get("resourceLocation") or properties.get("targetResourceLocation")
    return snapshot


class _EntityWait(Operation[Any]):
    """One wait on an operation entity: each poll re-reads it.

    A transient ``404`` is turned into a retry marker here rather than raised, so
    the engine stays free of exception policy: a step answers what it saw.
    """

    def __init__(self, entity: "ClientObject", **options: Any) -> None:
        options.setdefault("transient_statuses", TRANSIENT_POLL_STATUSES)
        super().__init__(**options)
        self._entity = entity

    def _step(self) -> OperationStatus:
        try:
            return operation_snapshot(self._entity, reload_operation(self._entity))
        except ClientRequestException as ex:
            return self._gap(ex)

    async def _step_async(self) -> OperationStatus:
        try:
            return operation_snapshot(self._entity, await reload_operation_async(self._entity))
        except ClientRequestException as ex:
            return self._gap(ex)

    def _observable(self, status: OperationStatus) -> bool:
        """A gap observes nothing: the entity was not there to report on."""
        return status.http_status not in _GAP_STATUSES

    def _outcome(self, status: OperationStatus) -> Any:
        """The entity, refreshed to its terminal state."""
        return self._entity

    def _gap(self, ex: ClientRequestException) -> OperationStatus:
        """Turn a transient poll failure into a retry marker; re-raise the rest."""
        if not is_transient_poll_error(ex) or ex.response is None:
            raise ex
        marker = OperationStatus.from_response(ex.response)
        if marker.retry_after is None:
            marker.retry_after = response_retry_after(ex.response)
        return marker


class PollableOperation:
    """Mixin that makes an entity with a ``status`` property awaitable.

    Host classes (``ClientObject`` subclasses) provide the entity fields; the
    mixin adds the lifecycle — :meth:`wait` / :meth:`wait_async` to run the work
    to completion, :meth:`stream` / :meth:`astream` to follow it — plus the
    :attr:`is_operation_complete` / :attr:`is_operation_failed` helpers.
    """

    #: Seconds between polls when the server sends no ``Retry-After``.
    operation_polling_interval: float = 10.0

    #: Maximum seconds to wait before raising :class:`OperationTimeoutError`.
    operation_polling_timeout: float = 1800.0

    #: The wait in flight (or the last one run), so :meth:`cancel` can reach it.
    _operation_wait: "_EntityWait | None" = None

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
        sleep: Callable[[float], None] | None = None,
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
            sleep: Override the wait between polls. By default the wait is the
                interruptible one, so :meth:`cancel` wakes it immediately; pass a
                callable to take over (tests).

        Returns:
            ``self``, refreshed to its terminal state.

        Raises:
            OperationFailedError: On a failed terminal status (unless disabled).
            OperationTimeoutError: When the deadline elapses first.
        """
        self._operation(
            timeout=timeout,
            interval=interval,
            on_progress=on_progress,
            clock=clock,
            sleep=sleep,
        ).wait(raise_on_failure=raise_on_failure)
        return cast(Self, self)

    def stream(
        self,
        *,
        timeout: float | None = None,
        interval: float | None = None,
        on_progress: Callable[[OperationStatus], None] | None = None,
        clock: Callable[[], float] = time.monotonic,
        sleep: Callable[[float], None] | None = None,
    ) -> Iterator[OperationStatus]:
        """Re-fetch and yield every snapshot until the operation is terminal.

        The loop :meth:`wait` runs, exposed as an iterator — for a progress bar,
        a stall display, or a worker that logs each step. Nothing is raised for a
        failed or cancelled outcome; the caller sees it.
        """
        return self._operation(
            timeout=timeout,
            interval=interval,
            on_progress=on_progress,
            clock=clock,
            sleep=sleep,
        ).stream()

    async def wait_async(
        self,
        *,
        timeout: float | None = None,
        interval: float | None = None,
        on_progress: Callable[[OperationStatus], None] | None = None,
        raise_on_failure: bool = True,
        clock: Callable[[], float] = time.monotonic,
        async_sleep: Callable[[float], Any] | None = None,
    ) -> Self:
        """Await the operation until it is terminal, without blocking the loop.

        Async twin of :meth:`wait`; the delay between polls yields to the event
        loop so concurrently-running tasks keep making progress.
        """
        await self._operation(
            timeout=timeout,
            interval=interval,
            on_progress=on_progress,
            clock=clock,
            async_sleep=async_sleep,
        ).wait_async(raise_on_failure=raise_on_failure)
        return cast(Self, self)

    def astream(
        self,
        *,
        timeout: float | None = None,
        interval: float | None = None,
        on_progress: Callable[[OperationStatus], None] | None = None,
        clock: Callable[[], float] = time.monotonic,
        async_sleep: Callable[[float], Any] | None = None,
    ) -> AsyncIterator[OperationStatus]:
        """Await polling and yield every snapshot (async twin of :meth:`stream`)."""
        return self._operation(
            timeout=timeout,
            interval=interval,
            on_progress=on_progress,
            clock=clock,
            async_sleep=async_sleep,
        ).astream()

    def cancel(self) -> None:
        """Stop waiting at the next poll boundary.

        Cooperative, and **not** a rollback: work the service already applied
        remains. An operation entity has no generic cancel request — a service
        that has one exposes it as its own method — so this only stops *waiting*;
        the service operation keeps running.
        """
        if self._operation_wait is not None:
            self._operation_wait.cancel()

    async def cancel_async(self) -> None:
        """Async twin of :meth:`cancel`."""
        if self._operation_wait is not None:
            await self._operation_wait.cancel_async()

    # -- internals ---------------------------------------------------------

    def _operation(
        self,
        *,
        timeout: float | None,
        interval: float | None,
        on_progress: Callable[[OperationStatus], None] | None,
        clock: Callable[[], float],
        sleep: Callable[[float], None] | None = None,
        async_sleep: Callable[[float], Any] | None = None,
    ) -> "_EntityWait":
        """Build the wait for this entity, remembering it so :meth:`cancel` can reach it."""
        operation = _EntityWait(
            cast("ClientObject", self),
            interval=self.operation_polling_interval if interval is None else interval,
            timeout=self.operation_polling_timeout if timeout is None else timeout,
            on_progress=on_progress,
            clock=clock,
            sleep=sleep,
            async_sleep=async_sleep,
        )
        self._operation_wait = operation
        return operation

    def _operation_snapshot(self, response: Response | None = None) -> OperationStatus:
        """Build a snapshot from the refreshed entity (falling back to its properties)."""
        return operation_snapshot(cast("ClientObject", self), response)
