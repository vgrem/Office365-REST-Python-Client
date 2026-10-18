from __future__ import annotations

import asyncio
import threading
from abc import ABC, abstractmethod
from collections import deque
from contextlib import contextmanager
from typing import TYPE_CHECKING, Any, Callable, Iterator, List, Optional, Tuple, Type

from requests import Response
from typing_extensions import Self

from office365.runtime.client_request import ClientRequest
from office365.runtime.client_request_exception import ClientRequestException
from office365.runtime.client_result import ClientResult
from office365.runtime.http.http_method import HttpMethod
from office365.runtime.http.request_options import RequestOptions
from office365.runtime.limits import Limit, LimitDecl, collect_class_limits, collect_limit_meta
from office365.runtime.queries.client_query import ClientQuery
from office365.runtime.queries.read_entity import ReadEntityQuery
from office365.runtime.retry import DEFAULT_RETRY_EXCEPTIONS
from office365.runtime.transport.offload import run_offloaded

if TYPE_CHECKING:
    from office365.runtime.client_object import ClientObject
    from office365.runtime.http.throttling import RateLimiter
    from office365.runtime.queries.batch import BatchQuery


class ClientRuntimeContext(ABC):
    """Abstract base class for client runtime context.

    Provides core functionality for executing queries and managing request lifecycle.
    """

    _limit_meta: dict[str, Tuple[LimitDecl, ...]] = {}
    _class_limit_decls: Tuple[LimitDecl, ...] = ()

    def __init_subclass__(cls, **kwargs: object) -> None:
        super().__init_subclass__(**kwargs)
        cls._limit_meta = collect_limit_meta(cls)
        cls._class_limit_decls = collect_class_limits(cls)

    def __init__(self) -> None:
        self._queries: deque[ClientQuery] = deque()
        self._current_query = None
        self._pending_request: ClientRequest | None = None
        # Guards ``_current_query`` while a query's pre/post handlers run. Batch
        # execution sets it per sub-query (including on worker threads), so query
        # handlers keyed on ``current_query`` resolve to the right query.
        self._current_query_lock = threading.RLock()
        # True while :meth:`execute_query_retry` drives the retry loop, so the
        # public ``execute_query`` it calls runs the queue once (no recursion).
        # The client-level retry policy itself lives on the pending
        # ``ClientRequest`` (a transport/resilience setting).
        self._in_retry = False
        # Failure sink for :meth:`collect_batch_failures`; ``None`` outside a
        # tolerant scope, which is what keeps the default batch semantics
        # (a failed sub-request raises) untouched.
        self._batch_failures: list[tuple[ClientQuery, ClientRequestException]] | None = None

    @contextmanager
    def collect_batch_failures(self) -> Iterator[list[tuple[ClientQuery, ClientRequestException]]]:
        """Run batched writes tolerantly: a rejected sub-request is recorded, not raised.

        Inside the scope, a sub-request the service rejects (a denied write, a
        validation error) no longer aborts the batch: it is appended to the
        yielded list as ``(query, exception)`` and the remaining sub-requests
        still run. Throttled sub-requests (HTTP 429/503) are retried exactly as
        outside the scope; if a retry is exhausted the failure is recorded too.

        Failure attribution is per *query*: the sink is keyed on the context, so
        it survives batch partitioning, splitting and per-sub-request retries.
        Pair each queued query with the item it writes, then match it against the
        recorded failures to report per item instead of failing the whole run.

        Example:
            >>> with ctx.collect_batch_failures() as failures:
            ...     for name in link_names:
            ...         content_type.field_links.add(name)
            ...     ctx.execute_batch()
            >>> for query, error in failures:
            ...     print(query, error)

        Yields:
            The list the failures are appended to, as ``(query, exception)`` pairs
            in completion order (unordered when ``concurrency`` > 1).

        Raises:
            RuntimeError: If a tolerant scope is already active on this context.
        """
        if self._batch_failures is not None:
            raise RuntimeError("a tolerant batch scope is already active on this context")
        failures: list[tuple[ClientQuery, ClientRequestException]] = []
        self._batch_failures = failures
        try:
            yield failures
        finally:
            self._batch_failures = None

    @property
    def collecting_batch_failures(self) -> bool:
        """Whether a :meth:`collect_batch_failures` scope is active on this context."""
        return self._batch_failures is not None

    @classmethod
    def declared_limits(cls) -> Tuple[Limit, ...]:
        """The limits declared on this class and its methods/properties (``@limit``)."""
        class_limits = tuple(decl.limit for decl in cls._class_limit_decls)
        member_limits = tuple(decl.limit for decls in cls._limit_meta.values() for decl in decls)
        return (*class_limits, *member_limits)

    @property
    def service_root_url(self) -> str:
        """Get the API service root URL"""
        return self.pending_request().service_root_url

    @property
    def current_query(self) -> ClientQuery | None:
        return self._current_query

    @property
    def last_query(self) -> ClientQuery | None:
        """The most recently queued (still pending) query, or ``None``.

        Lets a builder method associate metadata with the query it just created
        -- ``@require_permission`` stamps its requirement here so a later denial
        can explain which permission was missing.
        """
        return self._queries[-1] if self._queries else None

    @contextmanager
    def current_query_scope(self, query: ClientQuery) -> Iterator[None]:
        """Expose ``query`` as :attr:`current_query` while executing a block.

        Query handlers (``before_execute`` / ``after_execute`` / ``on_error``)
        are keyed on ``current_query``; batch execution bypasses the normal
        ``_get_next_query`` cursor, so it uses this scope to make those handlers
        resolve to the sub-query being built or applied. The lock keeps the
        assignment safe when independent batches run on a thread pool.

        Args:
            query: The query to expose for the duration of the block.
        """
        with self._current_query_lock:
            previous = self._current_query
            self._current_query = query
            try:
                yield
            finally:
                self._current_query = previous

    @property
    def has_pending_request(self) -> bool:
        """Whether there are pending queries to execute."""
        return len(self._queries) > 0

    def execute_query_retry(
        self,
        max_retry: int = 5,
        timeout_secs: int = 5,
        max_delay: Optional[int] = None,
        jitter: bool = True,
        success_callback: Optional[Callable[[ClientObject | None], None]] = None,
        failure_callback: Optional[Callable[[int, Exception], Optional[int]]] = None,
        exceptions: Tuple[Type[Exception], ...] = DEFAULT_RETRY_EXCEPTIONS,
        is_retriable: Optional[Callable[[Exception], bool]] = None,
    ) -> None:
        """Executes pending queries with retry logic.

        Only transient failures (HTTP 408/429/500/502/503/504 or non-HTTP errors)
        are retried. Permanent failures (e.g. HTTP 400/401/403/404) are re-raised
        immediately, and the last exception is re-raised once retries are exhausted.

        Delays between attempts use exponential backoff with jitter; a delay
        returned by ``failure_callback`` (e.g. the server's ``Retry-After`` via
        ``retry_after_delay``) overrides the backoff.

        Args:
            max_retry: Maximum number of retry attempts
            timeout_secs: Base delay for exponential backoff (seconds)
            max_delay: Optional cap on the exponential delay (seconds)
            jitter: Whether to randomize the delay (default True)
            success_callback: Called on successful execution
            failure_callback: Called after each failed attempt; may return a
                retry delay in seconds to override the backoff
            exceptions: Exception types that trigger retries
            is_retriable: Optional predicate deciding whether a caught exception
                is retried. Defaults to :func:`~office365.runtime.retry.is_transient_error`;
                pass :func:`~office365.runtime.retry.retry_on` to also retry
                otherwise-permanent errors such as a locked file (HTTP 423).
        """
        from office365.runtime.retry import is_transient_error, retry, should_reset_connections

        def _on_failure(_attempt: int, ex: Exception) -> Optional[int]:
            # Drop a poisoned keep-alive socket before retrying a 503/connection
            # failure (Graph best practices: back off and use a new connection).
            if should_reset_connections(ex):
                self.pending_request().transport.reset_connections()
            # Re-queue the failed query for a retry, except on the last attempt —
            # otherwise the context is left with a stale, un-executed query.
            if _attempt < max_retry and self.current_query is not None:
                self.add_query(self.current_query)
            return failure_callback(_attempt, ex) if callable(failure_callback) else None

        def _on_success(_) -> None:
            if callable(success_callback) and self.current_query is not None:
                success_callback(self.current_query.return_type)

        self._in_retry = True
        try:
            retry(
                self.execute_query,
                max_retry=max_retry,
                timeout_secs=timeout_secs,
                max_delay=max_delay,
                jitter=jitter,
                exceptions=exceptions,
                is_retriable=is_retriable or is_transient_error,
                on_failure=_on_failure,
                on_success=_on_success,
            )
        except BaseException:
            self._clear_retry_state()
            raise
        finally:
            self._in_retry = False

    def _clear_retry_state(self) -> None:
        """Undo any failed-query re-queue and reset the cursor after an error.

        Called when ``execute_query_retry`` exits by exception so the context is
        never left dirty (a re-queued query would otherwise be re-run on reuse).
        """
        current = self._current_query
        if current is not None and self._queries and self._queries[-1] is current:
            self._queries.pop()
        self._current_query = None

    def __enter__(self) -> Self:
        return self

    def close(self) -> None:
        """Release the transport's pooled connections.

        Equivalent to leaving a ``with`` block; call it explicitly when the
        context is created and disposed without the context-manager protocol.
        """
        self.pending_request().transport.close()

    async def aclose(self) -> None:
        """Async twin of :meth:`close`.

        Awaited by ``async with`` on exit; call it explicitly when shutting the
        client down outside the context-manager protocol. Native async
        transports release their own resources here (otherwise the synchronous
        :meth:`BaseTransport.close` is run in a worker thread).
        """
        await self.pending_request().async_transport.aclose()

    def __exit__(self, *args) -> None:
        self.close()

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(self, *args) -> None:
        await self.aclose()

    @abstractmethod
    def pending_request(self) -> ClientRequest:
        """Gets the pending client request."""

    def load(self, client_object: ClientObject, properties_to_retrieve: List[str] | None = None) -> Self:
        """Prepares retrieval query for the specified client object.

        Args:
            client_object: The client object to load
            properties_to_retrieve: Specific properties to retrieve

        Returns:
            Self for method chaining
        """
        qry = ReadEntityQuery(client_object, properties_to_retrieve)
        self.add_query(qry)
        return self

    def before_execute(self, action: Callable[[RequestOptions], None], once: bool = True) -> Self:
        """
        Attach an event handler which is triggered before query is submitted to server
        """
        if len(self._queries) == 0:
            return self
        query = self._queries[-1]

        self.pending_request().before_execute(
            action, once=once, condition=lambda: self.current_query is not None and self.current_query.id == query.id
        )
        return self

    def after_execute(
        self,
        action: Callable[[Any], Any],
        execute_first: bool = False,
        include_response: bool = False,
    ) -> Self:
        """Attaches post-query execution handler.

        Args:
            action: Callback to execute after query
            execute_first: Whether to prioritize this query
            include_response: Whether to pass raw response

        Returns:
            Self for method chaining
        """
        if len(self._queries) == 0:
            return self
        query = self._queries[-1]

        def _process_response(resp: Response) -> None:
            resp.raise_for_status()
            if callable(action):
                action(resp if include_response else query.return_type)

        self.pending_request().after_execute(
            _process_response,
            once=True,
            condition=lambda: self.current_query is not None and self.current_query.id == query.id,
        )

        if execute_first and len(self._queries) > 1:
            self._queries.appendleft(self._queries.pop())

        return self

    def on_error(self, action: Callable[[ClientRequestException], None], once: bool = True) -> Self:
        """Attach an error handler for the pending query — a matching error is swallowed.

        This is a control hook (see :meth:`ClientRequest.on_error`): when the
        pending query fails and this handler's condition matches, the error is
        considered handled and does not re-raise. Use ``after_execute`` /
        ``throttle_guard`` for observation.
        """
        if len(self._queries) == 0:
            return self
        query = self._queries[-1]

        self.pending_request().on_error(
            action,
            once=once,
            condition=lambda: self.current_query is not None and self.current_query.id == query.id,
        )
        return self

    def execute_request_direct(self, path: str) -> Response:
        """Executes request directly against the specified path.

        Args:
            path: The URL path to request

        Returns:
            Raw response from server
        """
        return self.pending_request().execute_request(path)

    async def execute_request_direct_async(self, path: str) -> Response:
        """Executes request directly against the specified path, without blocking the loop.

        Async counterpart of :meth:`execute_request_direct`.

        Args:
            path: The URL path to request

        Returns:
            Raw response from server
        """
        return await self.pending_request().execute_request_async(path)

    @property
    def rate_limiter(self) -> "RateLimiter | None":
        """The shared rate limiter pacing this context's requests, if any.

        Returns ``None`` until :meth:`with_rate_limit` (or a shared limiter via
        ``ClientRequest.with_rate_limiter``) is configured.
        """
        return self.pending_request().rate_limiter

    def with_rate_limit(
        self,
        health_threshold: int = 80,
        min_interval: float = 0.0,
        per_scope: bool = False,
    ) -> Self:
        """Enable fleet-wide pacing for this context (opt-in).

        Wraps the context transport with a shared rate limiter, so every request
        — including the parallel batches dispatched by ``execute_batch`` — is
        gated by ``Retry-After`` / ``X-SharePointHealthScore`` as a group. Call
        this after any transport configuration (``with_transport``).

        Args:
            health_threshold: Health score at/above which the group paces.
            min_interval: Minimum pause applied on a high health score (seconds).
            per_scope: When ``True``, a Graph ``x-ms-throttle-scope`` pauses only
                requests tagged with that same ``RequestOptions.throttle_scope``
                instead of the whole fleet.

        Returns:
            Self: Supports method chaining
        """
        self.pending_request().with_rate_limit(
            health_threshold=health_threshold, min_interval=min_interval, per_scope=per_scope
        )
        return self

    def with_client_request_id(self, enabled: bool = True) -> Self:
        """Enable or disable the per-request ``client-request-id`` header.

        When enabled (the default) every request — including each sub-request of
        a batch — carries a fresh GUID for server-side log correlation, per the
        Microsoft Graph best practice. Pass ``False`` to opt out.

        Args:
            enabled: ``True`` to send the header (default), ``False`` to omit it.

        Returns:
            Self: Supports method chaining
        """
        self.pending_request().with_client_request_id(enabled)
        return self

    @property
    def auto_retry(self) -> bool:
        """Whether a client-level retry policy is active (see :meth:`with_auto_retry`)."""
        return self.pending_request().auto_retry

    def with_auto_retry(
        self,
        max_retry: int = 5,
        timeout_secs: int = 5,
        max_delay: Optional[int] = None,
        jitter: bool = True,
        exceptions: Tuple[Type[Exception], ...] = DEFAULT_RETRY_EXCEPTIONS,
        is_retriable: Optional[Callable[[Exception], bool]] = None,
    ) -> Self:
        """Make ``execute_query`` retry transient failures automatically (opt-in).

        By default ``execute_query`` runs the pending queries once and raises on
        the first failure. After calling this, **every** ``execute_query`` /
        ``execute_query_async`` on the context retries transient failures
        (HTTP 408/429/5xx or a dropped connection) with exponential backoff and
        jitter, honoring the server's ``Retry-After`` header. Permanent failures
        (e.g. 400/401/403/404) still raise immediately.

        This is the client-level counterpart of the per-call
        :meth:`execute_query_retry`; the policy applies to every query on the
        context, including those issued internally by ``ClientObject`` /
        ``ClientResult`` helpers, so callers that build a deferred request
        anywhere keep the safety net without opting in at each call site.
        Call it after any transport configuration (``with_transport`` /
        ``with_rate_limit``) and chain it with the other ``with_*`` methods.

        Args:
            max_retry: Maximum number of retry attempts
            timeout_secs: Base delay for exponential backoff (seconds)
            max_delay: Optional cap on the exponential delay (seconds)
            jitter: Whether to randomize the delay (default True)
            exceptions: Exception types that trigger retries
            is_retriable: Optional predicate deciding whether a caught exception
                is retried. Defaults to
                :func:`~office365.runtime.retry.is_transient_error`; pass
                :func:`~office365.runtime.retry.retry_on` to also retry
                otherwise-permanent errors such as a locked file (HTTP 423).

        Returns:
            Self: Supports method chaining
        """
        self.pending_request().with_auto_retry(
            max_retry=max_retry,
            timeout_secs=timeout_secs,
            max_delay=max_delay,
            jitter=jitter,
            exceptions=exceptions,
            is_retriable=is_retriable,
        )
        return self

    def execute_query(self) -> Self:
        """Executes all pending queries.

        When :meth:`with_auto_retry` has configured a client-level retry policy,
        transient failures are retried automatically (delegating to
        :meth:`execute_query_retry`); otherwise the pending queries run once.

        Returns:
            Self for method chaining
        """
        policy = self.pending_request().retry_policy
        if policy is not None and not self._in_retry:
            self.execute_query_retry(**policy)
            return self
        while self.has_pending_request:
            qry = self._get_next_query()
            qry.execute_query(self.pending_request())
        return self

    async def execute_query_async(self) -> Self:
        """Executes all pending queries without blocking the event loop.

        Async counterpart of :meth:`execute_query`: queries are awaited in
        submission order on the current task. Each call drains the context's
        pending queue, so to overlap independent requests either run them on
        separate contexts (see :meth:`clone`), use
        :meth:`execute_query_parallel_async` with ``concurrency`` > 1, or use
        :meth:`execute_batch_async` with ``concurrency`` > 1.

        When :meth:`with_auto_retry` is configured, transient failures are
        retried (delegating to :meth:`execute_query_async_retry`).

        Returns:
            Self for method chaining
        """
        policy = self.pending_request().retry_policy
        if policy is not None and not self._in_retry:
            await self.execute_query_async_retry(**policy)
            return self
        while self.has_pending_request:
            qry = self._get_next_query()
            try:
                await qry.execute_query_async(self.pending_request())
            except BaseException:
                # Cancelled/aborted mid-query: put the in-flight query back at
                # the front and drop the stale cursor, mirroring the parallel
                # paths, so a later ``execute_query_async`` resumes it.
                self._queries.appendleft(qry)
                self._current_query = None
                raise
        return self

    async def execute_query_async_retry(
        self,
        max_retry: int = 5,
        timeout_secs: int = 5,
        max_delay: Optional[int] = None,
        jitter: bool = True,
        success_callback: Optional[Callable[[ClientObject | None], None]] = None,
        failure_callback: Optional[Callable[[int, Exception], Optional[int]]] = None,
        exceptions: Tuple[Type[Exception], ...] = DEFAULT_RETRY_EXCEPTIONS,
        is_retriable: Optional[Callable[[Exception], bool]] = None,
    ) -> None:
        """Executes pending queries with retry logic, without blocking the loop.

        Async counterpart of :meth:`execute_query_retry` — same retry policy
        (transient-only by default, exponential backoff with jitter), but the
        delay between attempts uses ``asyncio.sleep``.

        Args:
            max_retry: Maximum number of retry attempts
            timeout_secs: Base delay for exponential backoff (seconds)
            max_delay: Optional cap on the exponential delay (seconds)
            jitter: Whether to randomize the delay (default True)
            success_callback: Called on successful execution
            failure_callback: Called after each failed attempt; may return a
                retry delay in seconds to override the backoff
            exceptions: Exception types that trigger retries
            is_retriable: Optional predicate deciding whether a caught exception
                is retried. Defaults to
                :func:`~office365.runtime.retry.is_transient_error`.
        """
        from office365.runtime.retry import is_transient_error, retry_async, should_reset_connections

        def _on_failure(_attempt: int, ex: Exception) -> Optional[int]:
            # Drop a poisoned keep-alive socket before retrying a 503/connection
            # failure (Graph best practices: back off and use a new connection).
            if should_reset_connections(ex):
                self.pending_request().async_transport.reset_connections()
            # Re-queue the failed query for a retry, except on the last attempt —
            # otherwise the context is left with a stale, un-executed query.
            if _attempt < max_retry and self.current_query is not None:
                self.add_query(self.current_query)
            return failure_callback(_attempt, ex) if callable(failure_callback) else None

        def _on_success(_) -> None:
            if callable(success_callback) and self.current_query is not None:
                success_callback(self.current_query.return_type)

        self._in_retry = True
        try:
            await retry_async(
                self.execute_query_async,
                max_retry=max_retry,
                timeout_secs=timeout_secs,
                max_delay=max_delay,
                jitter=jitter,
                exceptions=exceptions,
                is_retriable=is_retriable or is_transient_error,
                on_failure=_on_failure,
                on_success=_on_success,
            )
        except BaseException:
            self._clear_retry_state()
            raise
        finally:
            self._in_retry = False

    def _restore_pending(self, prepared: List[Tuple[ClientQuery, RequestOptions]]) -> None:
        """Re-queue popped queries in their original order after an aborted run.

        :meth:`execute_query_parallel` / :meth:`execute_query_parallel_async`
        pop queries off the queue before fan-out. When the run aborts
        (``BaseException`` / cancellation), the queries that were never applied
        are put back at the front so a later ``execute_query`` can retry them.
        """
        for qry, _options in reversed(prepared):
            self._queries.appendleft(qry)

    def execute_query_parallel(
        self,
        concurrency: int = 4,
        progress: Optional[Callable[[Any], None]] = None,
        max_retry: int = 5,
        timeout_secs: int = 5,
        max_delay: Optional[int] = None,
        jitter: bool = True,
        on_error: Optional[Callable[[ClientQuery, BaseException], None]] = None,
    ) -> Self:
        """Executes pending queries concurrently, overlapping their HTTP I/O.

        Intended for **independent** queries (e.g. bulk downloads: queue each
        ``item.download(f)`` then call this once). Query lifecycle stays on the
        calling thread — ``before_execute``/``after_execute``/``on_error`` hooks
        fire as usual — only the network round-trips run on the pool. Transient
        failures (408/429/5xx) are retried per query, honoring ``Retry-After``.

        Falls back to sequential :meth:`execute_query` when ``concurrency <= 1``
        or when the context uses a non-standard request (e.g. an upload session).

        Args:
            concurrency: Maximum number of concurrent requests.
            progress: Optional hook fired per completed query with a ``Progress``
              snapshot (``done``/``total``).
            max_retry: Maximum retry attempts per query.
            timeout_secs: Base delay for exponential backoff (seconds).
            max_delay: Optional cap on the exponential delay (seconds).
            jitter: Whether to randomize the backoff delay.
            on_error: Optional collector invoked as ``(query, error)`` for each
              failed query. When given, a permanent failure no longer aborts the
              batch and is not re-queued — execution continues with the remaining
              queries (used by bulk download to continue-and-report).

        Returns:
            Self for method chaining
        """
        if (concurrency <= 1 and on_error is None) or not self.has_pending_request:
            return self.execute_query()

        request = self.pending_request()
        if type(request).execute_query is not ClientRequest.execute_query:
            return self.execute_query()

        from office365.runtime.parallel import run_parallel

        def _send(_ctx, task: Tuple[ClientQuery, RequestOptions]):
            return self._send_with_retry(request, task[1], max_retry, timeout_secs, max_delay, jitter)

        while self.has_pending_request:
            prepared: List[Tuple[ClientQuery, RequestOptions]] = []
            while self.has_pending_request:
                qry = self._get_next_query()
                if type(qry).execute_query is not ClientQuery.execute_query:
                    qry.execute_query(request)  # deferred/no-op queries stay sequential
                    continue
                options = request.build_request(qry)
                request.beforeExecute(options)
                prepared.append((qry, options))
            if not prepared:
                break

            processed = 0
            try:
                responses = run_parallel(
                    _send,
                    prepared,
                    concurrency=concurrency,
                    progress=progress,
                    on_error=lambda _task, error: error,
                )

                for index, ((qry, _options), response) in enumerate(zip(prepared, responses)):
                    if isinstance(response, BaseException):
                        if on_error is not None:
                            on_error(qry, response)
                            processed = index + 1
                            continue
                        for pending, _ in prepared[index:]:  # keep failed + unhandled queries
                            self._queries.append(pending)
                        processed = len(prepared)
                        self._current_query = None
                        raise response
                    self._current_query = qry
                    if on_error is None:
                        request._raise_for_status(response)
                        request.process_response(response, qry)
                        request.afterExecute(response)
                        processed = index + 1
                        continue
                    try:
                        request._raise_for_status(response)
                        request.process_response(response, qry)
                        request.afterExecute(response)
                    except BaseException as error:  # noqa: BLE001 - collected, batch continues
                        on_error(qry, error)
                    processed = index + 1
            except BaseException:
                # Aborted mid-run (e.g. cancellation/interrupt): restore the
                # queries that were not applied so the caller can retry them.
                self._restore_pending(prepared[processed:])
                self._current_query = None
                raise
        self._current_query = None
        return self

    async def execute_query_parallel_async(
        self,
        concurrency: int = 4,
        progress: Optional[Callable[[Any], None]] = None,
        max_retry: int = 5,
        timeout_secs: int = 5,
        max_delay: Optional[int] = None,
        jitter: bool = True,
        on_error: Optional[Callable[[ClientQuery, BaseException], None]] = None,
    ) -> Self:
        """Executes pending queries concurrently without blocking the event loop.

        Async counterpart of :meth:`execute_query_parallel` with identical
        semantics — same bounded concurrency, per-query retry honoring
        ``Retry-After``, and ``progress`` snapshots. Intended for **independent**
        queries (e.g. bulk downloads: queue each ``item.download(f)`` then await
        this once). Query lifecycle stays on the event-loop thread —
        ``before_execute``/``after_execute``/``on_error`` hooks fire as usual —
        only the awaiting of the network round-trips overlaps.

        Requests are sent through each request's
        :attr:`~office365.runtime.client_request.ClientRequest.async_transport`,
        so a native async engine configured via
        :meth:`~office365.runtime.client_request.ClientRequest.with_async_transport`
        (e.g. ``HttpxTransport``) is used when present; otherwise the default
        transport offloads the blocking call to a worker thread.

        Falls back to sequential :meth:`execute_query_async` when ``concurrency
        <= 1`` or when the context uses a non-standard request (e.g. an upload
        session).

        Args:
            concurrency: Maximum number of concurrent requests.
            progress: Optional hook fired per completed query with a ``Progress``
              snapshot (``done``/``total``).
            max_retry: Maximum retry attempts per query.
            timeout_secs: Base delay for exponential backoff (seconds).
            max_delay: Optional cap on the exponential delay (seconds).
            jitter: Whether to randomize the backoff delay.
            on_error: Optional collector invoked as ``(query, error)`` for each
              failed query. When given, a permanent failure no longer aborts the
              batch and is not re-queued — execution continues with the remaining
              queries (used by bulk download to continue-and-report).

        Returns:
            Self for method chaining
        """
        if (concurrency <= 1 and on_error is None) or not self.has_pending_request:
            return await self.execute_query_async()

        request = self.pending_request()
        if type(request).execute_query is not ClientRequest.execute_query:
            return await self.execute_query_async()

        while self.has_pending_request:
            prepared: List[Tuple[ClientQuery, RequestOptions]] = []
            while self.has_pending_request:
                qry = self._get_next_query()
                if type(qry).execute_query is not ClientQuery.execute_query:
                    await qry.execute_query_async(request)  # deferred/no-op queries stay sequential
                    continue
                options = request.build_request(qry)
                await request.before_execute_async(options)
                prepared.append((qry, options))
            if not prepared:
                break

            processed = 0
            try:
                responses = await self._run_parallel_async(
                    request,
                    prepared,
                    concurrency=concurrency,
                    progress=progress,
                    max_retry=max_retry,
                    timeout_secs=timeout_secs,
                    max_delay=max_delay,
                    jitter=jitter,
                )

                for index, ((qry, _options), response) in enumerate(zip(prepared, responses)):
                    if isinstance(response, BaseException):
                        if on_error is not None:
                            on_error(qry, response)
                            processed = index + 1
                            continue
                        for pending, _ in prepared[index:]:  # keep failed + unhandled queries
                            self._queries.append(pending)
                        processed = len(prepared)
                        self._current_query = None
                        raise response
                    self._current_query = qry
                    if on_error is None:
                        request._raise_for_status(response)
                        request.process_response(response, qry)
                        request.afterExecute(response)
                        processed = index + 1
                        continue
                    try:
                        request._raise_for_status(response)
                        request.process_response(response, qry)
                        request.afterExecute(response)
                    except BaseException as error:  # noqa: BLE001 - collected, batch continues
                        on_error(qry, error)
                    processed = index + 1
            except BaseException:
                # Cancelled/aborted mid-run: restore unapplied queries and drop
                # the (now-stale) current query so a retry starts clean.
                self._restore_pending(prepared[processed:])
                self._current_query = None
                raise
        self._current_query = None
        return self

    async def _run_parallel_async(
        self,
        request: ClientRequest,
        prepared: List[Tuple[ClientQuery, RequestOptions]],
        *,
        concurrency: int,
        progress: Optional[Callable[[Any], None]],
        max_retry: int,
        timeout_secs: int,
        max_delay: Optional[int],
        jitter: bool,
    ) -> List[Any]:
        """Send ``prepared`` requests concurrently, returning results/errors in input order.

        Each task stores its outcome (a response or the raised exception) at its
        index so the caller can apply responses in queue order; ``progress``
        fires live as each task settles.
        """
        from office365.runtime.operations import Progress

        semaphore = asyncio.Semaphore(concurrency)
        results: List[Any] = [None] * len(prepared)
        total = len(prepared)

        async def _run(index: int, options: RequestOptions) -> int:
            async with semaphore:
                try:
                    results[index] = await self._send_with_retry_async(
                        request, options, max_retry, timeout_secs, max_delay, jitter
                    )
                except Exception as e:  # noqa: BLE001 — surfaced in order by the caller
                    results[index] = e
            return index

        tasks = [asyncio.ensure_future(_run(index, options)) for index, (_qry, options) in enumerate(prepared)]
        done = 0
        try:
            for coro in asyncio.as_completed(tasks):
                index = await coro
                done += 1
                if callable(progress):
                    progress(Progress(done=done, total=total, stage="parallel", items=[results[index]]))
        finally:
            # On cancellation/abort, stop the sibling requests still in flight so
            # they cannot outlive the caller (and keep consuming the connection
            # pool) after this coroutine unwinds.
            if not all(task.done() for task in tasks):
                for task in tasks:
                    task.cancel()
                await asyncio.gather(*tasks, return_exceptions=True)
        return results

    @staticmethod
    def _send_with_retry(
        request: ClientRequest,
        options: RequestOptions,
        max_retry: int,
        timeout_secs: int,
        max_delay: Optional[int],
        jitter: bool,
    ):
        """Send one prepared request, retrying transient failures per ``Retry-After``."""
        from office365.runtime.retry import (
            TRANSIENT_STATUS_CODES,
            response_retry_after,
            retry,
            should_reset_connections,
        )

        def _attempt():
            response = request.transport.execute(options)
            if response.status_code in TRANSIENT_STATUS_CODES:
                raise ClientRequestException.from_response(response)
            return response

        def _on_failure(_attempt_num: int, ex: Exception) -> Optional[int]:
            if should_reset_connections(ex):
                request.transport.reset_connections()
            return response_retry_after(getattr(ex, "response", None))

        return retry(
            _attempt,
            max_retry=max_retry,
            timeout_secs=timeout_secs,
            max_delay=max_delay,
            jitter=jitter,
            on_failure=_on_failure,
        )

    @staticmethod
    async def _send_with_retry_async(
        request: ClientRequest,
        options: RequestOptions,
        max_retry: int,
        timeout_secs: int,
        max_delay: Optional[int],
        jitter: bool,
    ):
        """Send one prepared request, retrying transient failures per ``Retry-After``.

        Async counterpart of :meth:`_send_with_retry`: awaits the request's
        async transport and backs off with ``asyncio.sleep`` so sibling tasks
        keep making progress.
        """
        from office365.runtime.retry import (
            TRANSIENT_STATUS_CODES,
            response_retry_after,
            retry_async,
            should_reset_connections,
        )

        async def _attempt():
            response = await request.async_transport.execute_async(options)
            if response.status_code in TRANSIENT_STATUS_CODES:
                raise ClientRequestException.from_response(response)
            return response

        def _on_failure(_attempt_num: int, ex: Exception) -> Optional[int]:
            if should_reset_connections(ex):
                request.async_transport.reset_connections()
            return response_retry_after(getattr(ex, "response", None))

        return await retry_async(
            _attempt,
            max_retry=max_retry,
            timeout_secs=timeout_secs,
            max_delay=max_delay,
            jitter=jitter,
            on_failure=_on_failure,
        )

    def add_query(self, query: ClientQuery) -> Self:
        """Adds a query to the pending queue.

        Args:
            query: The query to add

        Returns:
            Self for method chaining
        """
        self._queries.append(query)
        return self

    def clear(self) -> Self:
        """Clears pending state and resets the pending request.

        A new request is created lazily on the next call to ``pending_request()``.
        """
        self._current_query = None
        self._queries = deque()
        self._pending_request = None
        return self

    def get_metadata(self) -> ClientResult[bytes]:
        """Retrieves service metadata.

        Returns:
            ClientResult containing metadata XML
        """
        return_type = ClientResult(self, bytes())

        def _construct_request(request: RequestOptions) -> None:
            request.url += "/$metadata"
            request.method = HttpMethod.Get

        def _process_response(response: Response) -> None:
            return_type.set_property("__value", response.content)

        qry = ClientQuery(self)
        (self.add_query(qry).before_execute(_construct_request).after_execute(_process_response, include_response=True))
        return return_type

    def _get_next_query(self, count: int = 1) -> ClientQuery:
        """Gets the next query(s) to execute.

        Args:
            count: Number of queries to batch together

        Returns:
            The next query to execute
        """
        if count == 1:
            qry = self._queries.popleft()
        else:
            from office365.runtime.queries.batch import BatchQuery

            qry = BatchQuery(self)
            while self.has_pending_request and count > 0:
                qry.add(self._queries.popleft())
                count = count - 1
        self._current_query = qry
        return qry

    def _split_batches(
        self,
        items_per_batch: int,
        max_batch_bytes: Optional[int] = None,
    ) -> list["BatchQuery"]:
        """Drain the pending queue into independent batch units.

        Unlike ``_get_next_query``, this does not mutate ``_current_query``,
        making it safe to pre-split the queue before concurrent execution.
        Batches are capped by item count and (when ``max_batch_bytes`` is given)
        by estimated payload size — a single oversized query still goes alone.

        Args:
            items_per_batch: Maximum queries per batch
            max_batch_bytes: Maximum estimated batch payload size in bytes

        Returns:
            List of BatchQuery objects preserving submission order
        """
        from office365.runtime.odata.batch_util import partition_by_limits
        from office365.runtime.queries.batch import BatchQuery

        queries = []
        while self.has_pending_request:
            queries.append(self._queries.popleft())

        batches = []
        for chunk in partition_by_limits(queries, items_per_batch, max_batch_bytes):
            batches.append(BatchQuery(self, chunk))
        return batches

    def _execute_batches_in_parallel(
        self,
        batches: list["BatchQuery"],
        concurrency: int,
        success_callback: Optional[Callable[[List[Any]], None]] = None,
    ) -> None:
        """Execute batch units concurrently on a thread pool.

        Reuses the generic :func:`~office365.runtime.parallel.run_parallel`
        primitive; ``success_callback`` is invoked **live, as each batch
        completes** (on the calling thread), so callers can report progress.
        After the pool drains, the first failure is re-raised.

        Args:
            batches: Batch units to execute
            concurrency: Maximum number of concurrent batch requests
            success_callback: Called with each successfully completed batch's
                return types, in completion order
        """
        from office365.runtime.parallel import run_parallel

        errors: list[BaseException] = []

        def _on_progress(snapshot: Any) -> None:
            if not callable(success_callback):
                return
            for return_types in snapshot.items or []:
                if return_types is not None:
                    success_callback(return_types)

        def _on_error(_task: Any, error: BaseException) -> None:
            errors.append(error)

        run_parallel(
            lambda _ctx, batch_qry: self._execute_batch(batch_qry),
            batches,
            concurrency=concurrency,
            progress=_on_progress,
            on_error=_on_error,
        )
        if errors:
            raise errors[0]

    async def _execute_batch_async(self, batch_qry: "BatchQuery") -> List[Any]:
        """Execute a single batch unit without blocking the event loop.

        The synchronous batch machinery owns form-digest handling and
        per-sub-request retry, so the default async path runs :meth:`_execute_batch`
        in a worker thread. That keeps the loop free and lets independent batches
        overlap; a context with a native async batch stack can override this.
        """
        return await run_offloaded(self._execute_batch, batch_qry)

    async def _run_batches_async(
        self,
        batches: list["BatchQuery"],
        concurrency: int,
        success_callback: Optional[Callable[[List[Any]], None]] = None,
    ) -> None:
        """Execute batch units without blocking the loop.

        Async counterpart of :meth:`_execute_batches_in_parallel`: with
        ``concurrency`` > 1 batches overlap up to that limit, and
        ``success_callback`` is invoked as each batch completes. After all
        batches settle, the first failure is re-raised.

        Args:
            batches: Batch units to execute
            concurrency: Maximum number of concurrent batch requests
            success_callback: Called with each successfully completed batch's
                return types, in completion order
        """
        if concurrency <= 1:
            for qry in batches:
                return_types = await self._execute_batch_async(qry)
                if callable(success_callback) and return_types:
                    success_callback(return_types)
            return

        semaphore = asyncio.Semaphore(max(1, concurrency))
        errors: list[BaseException] = []

        async def _one(batch_qry: "BatchQuery") -> None:
            async with semaphore:
                try:
                    return_types = await self._execute_batch_async(batch_qry)
                except Exception as err:  # first error is re-raised after draining
                    errors.append(err)
                    return
                if callable(success_callback) and return_types:
                    success_callback(return_types)

        await asyncio.gather(*(_one(batch) for batch in batches))
        if errors:
            raise errors[0]

    def _execute_batch(self, batch_qry: "BatchQuery") -> List[Any]:
        """Execute a single batch unit (implemented by concrete contexts)."""
        raise NotImplementedError
