from __future__ import annotations

from collections.abc import Callable
from datetime import datetime

from typing_extensions import Self

from office365.entity import Entity
from office365.runtime.operation import OperationTimeoutError
from office365.runtime.pollable import PollableOperation, normalize_status
from office365.runtime.types.odata_property import odata
from office365.teams.operations.async_status import TeamsAsyncOperationStatus
from office365.teams.operations.error import OperationError
from office365.teams.operations.type import TeamsAsyncOperationType


def wait_for_operation(
    operation: "TeamsAsyncOperation",
    *,
    success_callback: Callable[["TeamsAsyncOperation"], None] | None = None,
    timeout_sec: int = 180,
    interval: int = 15,
) -> None:
    """Poll an async operation until ``succeeded``, blocking the calling thread.

    The status GETs run here rather than through the caller's queue, so this works
    both on its own and from inside an ``after_execute`` hook (where the one-shot
    convenience methods call it to chain submit → poll → reload). Raises when the
    operation fails or times out.

    Args:
        operation: The async operation to poll.
        success_callback: Called with the populated operation once succeeded.
        timeout_sec: Maximum seconds to wait.
        interval: Seconds between status polls.
    """

    def _on_failed(op) -> None:
        raise RuntimeError(f"Async operation failed: {op.status}")

    operation.poll_for_status(
        TeamsAsyncOperationStatus.succeeded,
        timeout_sec=timeout_sec,
        polling_interval=interval,
        success_callback=success_callback,
        failure_callback=_on_failed,
    )


async def wait_for_operation_async(
    operation: "TeamsAsyncOperation",
    *,
    success_callback: Callable[["TeamsAsyncOperation"], None] | None = None,
    timeout_sec: int = 180,
    interval: int = 15,
) -> "TeamsAsyncOperation":
    """Await an async operation until ``succeeded``.

    The awaitable twin of :func:`wait_for_operation`: each status GET yields to
    the event loop, so other tasks keep running while the (often minutes-long)
    Teams operation completes.

    Args:
        operation: The async operation to poll.
        success_callback: Called with the populated operation once succeeded.
        timeout_sec: Maximum seconds to wait.
        interval: Seconds between status polls.

    Returns:
        The populated operation (``succeeded``).

    Raises:
        RuntimeError: When the operation fails or times out.
    """

    def _on_failed(op) -> None:
        raise RuntimeError(f"Async operation failed: {op.status}")

    return await operation.poll_for_status_async(
        TeamsAsyncOperationStatus.succeeded,
        timeout_sec=timeout_sec,
        polling_interval=interval,
        success_callback=success_callback,
        failure_callback=_on_failed,
    )


class TeamsAsyncOperation(PollableOperation, Entity):
    """
    A Microsoft Teams async operation is an operation that transcends the lifetime of a single API request.
    These operations are long-running or too expensive to complete within the timeframe of their originating request.

    When an async operation is initiated, the method returns a 202 Accepted response code.
    The response will also contain a Location header, which contains the location of the teamsAsyncOperation.
    Periodically check the status of the operation by making a GET request to this location; wait >30 seconds
    between checks. When the request completes successfully, the status will be "succeeded" and
    the targetResourceLocation will point to the created/modified resource.

    """

    def poll_for_status(
        self,
        status_type: TeamsAsyncOperationStatus = TeamsAsyncOperationStatus.succeeded,
        timeout_sec: int = 180,
        polling_interval: int = 15,
        success_callback: Callable[[TeamsAsyncOperation], None] | None = None,
        failure_callback: Callable[[TeamsAsyncOperation], None] | None = None,
    ) -> Self:
        """Poll to check for completion of an async Teams operation (blocking).

        One poll re-reads the operation through the shared wait
        (`office365.runtime.operation.Operation`), so a transient ``404`` — the
        operation's location can be briefly unavailable right after the ``202``
        ("No workflow found with supplied ID") — is a polling gap, the deadline is
        measured on the clock, and the pause honours ``Retry-After``. Exactly one
        callback fires: success when the operation reached ``status_type``,
        otherwise failure (a failed status *or* the deadline).

        Args:
            status_type: The status to wait for (default succeeded)
            timeout_sec: Maximum seconds to wait (default 180)
            polling_interval: Seconds between polls (default 15)
            success_callback: Called on success with the populated operation
            failure_callback: Called on timeout or failed status
        """
        wait = self._operation(
            target_status=normalize_status(status_type),
            interval=float(polling_interval),
            timeout=float(timeout_sec),
        )
        try:
            # A failed status is *reported* to the callback, not raised: callers
            # such as ``wait_for_operation`` decide what failure means.
            wait.wait(raise_on_failure=False)
        except OperationTimeoutError:
            pass
        self._settle(status_type, success_callback, failure_callback)
        return self

    async def poll_for_status_async(
        self,
        status_type: TeamsAsyncOperationStatus = TeamsAsyncOperationStatus.succeeded,
        timeout_sec: int = 180,
        polling_interval: int = 15,
        success_callback: Callable[[TeamsAsyncOperation], None] | None = None,
        failure_callback: Callable[[TeamsAsyncOperation], None] | None = None,
    ) -> Self:
        """Async twin of :meth:`poll_for_status`, driven by ``await`` (no blocking).

        Performs the status ``GET`` and the delay between polls on the event loop,
        honoring ``Retry-After`` and treating a transient ``404`` as a polling gap.
        Callbacks receive the populated operation, exactly like the synchronous
        version.

        Args:
            status_type: The status to wait for (default ``succeeded``).
            timeout_sec: Maximum seconds to wait (default 180).
            polling_interval: Seconds between polls when no ``Retry-After`` is
                sent (default 15).
            success_callback: Called on success with the populated operation.
            failure_callback: Called on timeout or failed status.
        """
        wait = self._operation(
            target_status=normalize_status(status_type),
            interval=float(polling_interval),
            timeout=float(timeout_sec),
        )
        try:
            await wait.wait_async(raise_on_failure=False)
        except OperationTimeoutError:
            pass
        self._settle(status_type, success_callback, failure_callback)
        return self

    def _settle(
        self,
        status_type: TeamsAsyncOperationStatus,
        success_callback: Callable[[TeamsAsyncOperation], None] | None,
        failure_callback: Callable[[TeamsAsyncOperation], None] | None,
    ) -> None:
        """Fire exactly one terminal callback: success if the target was reached."""
        if normalize_status(self.operation_status) == normalize_status(status_type):
            if callable(success_callback):
                success_callback(self)
        elif callable(failure_callback):
            failure_callback(self)

    @odata(name="attemptsCount")
    @property
    def attempts_count(self) -> int | None:
        """Number of times the operation was attempted before being marked as succeeded or failed."""
        return self.properties.get("attemptsCount", None)

    @odata(name="createdDateTime")
    @property
    def created_date_time(self) -> datetime:
        """Date and time when the operation was created."""
        return self.properties.get("createdDateTime", datetime.min)

    @property
    def error(self) -> OperationError:
        """Error information if the operation failed."""
        return self.properties.get("error", OperationError())

    @odata(name="lastActionDateTime")
    @property
    def last_action_date_time(self) -> datetime:
        """Date and time when the operation was last updated."""
        return self.properties.get("lastActionDateTime", datetime.min)

    @odata(name="operationType")
    @property
    def operation_type(self) -> TeamsAsyncOperationType:
        """The type of the operation."""
        return self.properties.get("operationType", TeamsAsyncOperationType.unknown)

    @property
    def status(self) -> TeamsAsyncOperationStatus:
        """Operation status."""
        return self.properties.get("status", TeamsAsyncOperationStatus.invalid)

    @property
    def target_resource_id(self) -> str | None:
        """The ID of the object that's created or modified as result of this async operation, typically a team."""
        return self.properties.get("targetResourceId", None)

    @property
    def target_resource_location(self) -> str | None:
        """The location of the object that's created or modified as result of this async operation.
        This URL should be treated as an opaque value and not parsed into its component paths.
        """
        return self.properties.get("targetResourceLocation", None)
