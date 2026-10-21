"""Submit requests with ``Prefer: respond-async``.

Some Microsoft 365 services document the OData ``Prefer: respond-async``
preference on operations that may take longer than a single request (notably the
Excel workbook APIs and other long-running actions). Instead of holding the
connection open, the service answers ``202 Accepted`` with a ``Location`` header
pointing at an *operation-status* (monitor) URL. Requests that finish quickly are
answered normally, so the preference is a hint rather than a guarantee.

This module bridges that pair onto the generic poller in
:mod:`office365.runtime.lro`. It builds the request for a query, attaches the
preference, and executes it through the normal request pipeline (auth,
``client-request-id``, throttling) — then:

* returns a :class:`~office365.runtime.lro.LongRunningOperationResult` when the
  service accepted the request asynchronously; poll it with ``wait()`` /
  ``wait_async()``, or
* returns ``None`` when the service completed the request synchronously, after
  feeding the response into the query so its regular return value is populated.

Example::

    from office365.runtime.queries.create_entity import CreateEntityQuery
    from office365.runtime.respond_async import RespondAsyncRequest

    row = rows.create_typed_object()
    query = CreateEntityQuery(rows, row, row)
    operation = RespondAsyncRequest(context, query, wait=10).execute()
    if operation is not None:
        operation.wait()  # the server accepted the work asynchronously
"""

from __future__ import annotations

from http import HTTPStatus
from typing import TYPE_CHECKING, Any, Optional

from office365.runtime.http.prefer import prefer_respond_async
from office365.runtime.lro import LongRunningOperationResult, resolve_poll_url

if TYPE_CHECKING:
    from office365.runtime.client_runtime_context import ClientRuntimeContext
    from office365.runtime.queries.client_query import ClientQuery


class RespondAsyncRequest:
    """Execute a query with ``Prefer: respond-async`` and poll it if accepted.

    Args:
        context: The client runtime context that owns the credentials.
        query: A *fresh* query (not yet added to the context queue) whose
            ``return_type`` receives the result when the service answers
            synchronously.
        wait: Optional RFC 7240 ``wait`` preference (seconds) rendered as
            ``Prefer: respond-async, wait=N``.
        authenticate: Attach credentials when polling the monitor URL (default);
            Graph hands back authenticated monitor URLs for most operations.
        final_state_via: Which response header carries the monitor URL; one of
            ``"auto"`` (default), ``"operation-location"``, ``"azure-asyncoperation"``,
            ``"location"`` or ``"original-url"``.
    """

    def __init__(
        self,
        context: "ClientRuntimeContext",
        query: "ClientQuery[Any]",
        *,
        wait: Optional[int] = None,
        authenticate: bool = True,
        final_state_via: str = "auto",
    ) -> None:
        self._context = context
        self._query = query
        self._wait = wait
        self._authenticate = authenticate
        self._final_state_via = final_state_via

    def _build_request(self) -> Any:
        request = self._context.pending_request().build_request(self._query)
        prefer_respond_async(request, wait=self._wait)
        return request

    def _maybe_result(self, response: Any) -> LongRunningOperationResult | None:
        """Return a pollable result when ``response`` is an accepted ``202``."""
        # Bypass the query queue: the request is sent here, not by execute_query().
        if response.status_code != HTTPStatus.ACCEPTED:
            return None
        poll_url = resolve_poll_url(response, final_state_via=self._final_state_via)
        if poll_url is None:
            return None
        return LongRunningOperationResult(
            self._context,
            poll_url,
            authenticate=self._authenticate,
            final_state_via=self._final_state_via,
        )

    def _finish_sync(self, response: Any) -> None:
        request = self._context.pending_request()
        request.handle_response(response, self._query)
        request.afterExecute(response)

    def execute(self) -> LongRunningOperationResult | None:
        """Submit the query (blocking).

        Returns:
            A :class:`LongRunningOperationResult` when the service answered
            ``202 Accepted``; otherwise ``None`` and the query's ``return_type``
            holds the synchronous result.
        """
        request = self._build_request()
        response = self._context.pending_request().execute_request_direct(request)
        result = self._maybe_result(response)
        if result is None:
            self._finish_sync(response)
        return result

    async def execute_async(self) -> LongRunningOperationResult | None:
        """Submit the query without blocking the loop.

        Async twin of :meth:`execute`; awaits the transport. The returned result
        is polled with ``await result.wait_async()``.
        """
        request = self._build_request()
        response = await self._context.pending_request().execute_request_direct_async(request)
        result = self._maybe_result(response)
        if result is None:
            self._finish_sync(response)
        return result


__all__ = ["RespondAsyncRequest"]
