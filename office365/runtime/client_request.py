from __future__ import annotations

import uuid
from abc import ABC, abstractmethod
from typing import Any, Awaitable, Callable, Optional, Tuple, Type

import requests
from requests import HTTPError, Response
from typing_extensions import Self

from office365.runtime.client_request_exception import ClientRequestException
from office365.runtime.http.request_options import RequestOptions
from office365.runtime.http.throttling import RateLimiter
from office365.runtime.queries.client_query import ClientQuery
from office365.runtime.retry import DEFAULT_RETRY_EXCEPTIONS
from office365.runtime.transport.base import BaseTransport, NoTimeoutType
from office365.runtime.transport.offload import run_offloaded
from office365.runtime.transport.requests_transport import (
    DEFAULT_POOL_CONNECTIONS,
    DEFAULT_POOL_MAXSIZE,
    RequestsTransport,
)
from office365.runtime.transport.throttled_transport import ThrottledTransport
from office365.runtime.types.event_handler import EventHandler

#: Private :class:`~office365.runtime.http.request_options.RequestOptions`
#: attribute marking a request already authenticated by the async path, so the
#: synchronous auth hook (still run as an offloaded ``beforeExecute`` handler)
#: does not acquire a second token.
ASYNC_AUTHENTICATED_FLAG = "_office365_async_authenticated"


class ClientRequest(ABC):
    def __init__(self, transport: BaseTransport | None = None):
        self._transport = transport or RequestsTransport()
        self._async_transport: BaseTransport | None = None
        self._rate_limiter: RateLimiter | None = None
        self._client_request_id_enabled = True
        # Retry policy set by :meth:`with_auto_retry`; ``None`` means queries are
        # executed once. Stored here (not on the context) so the transport layer
        # owns resilience settings, next to the rate limiter, and so clones that
        # reuse this request inherit the policy.
        self._retry_policy: dict[str, Any] | None = None
        #: Optional awaitable auth hook (see ``before_execute_async``), used by
        #: requests whose credentials are supplied as an async token callback.
        self._async_authenticate: Optional[Callable[[RequestOptions], Awaitable[None]]] = None
        # Set by an ``on_error`` wrapper when its condition matches, so
        # ``execute_query`` can tell a handled failure from a stale handler that
        # merely happened to be registered (see :meth:`on_error`).
        self._error_handled = False
        self.beforeExecute: EventHandler[[RequestOptions]] = EventHandler()
        self.afterExecute: EventHandler[[Response]] = EventHandler()
        self.onError: EventHandler[[ClientRequestException]] = EventHandler()

    @property
    def transport(self) -> BaseTransport:
        """The HTTP transport used for API requests."""
        return self._transport

    @transport.setter
    def transport(self, value: BaseTransport) -> None:
        self._transport = value

    @property
    def async_transport(self) -> BaseTransport:
        """The transport backing ``execute_query_async``.

        Defaults to :attr:`transport`, so the async path reuses the same
        session. Set a dedicated transport via :meth:`with_async_transport` to
        run async requests through a native async engine while keeping the
        synchronous path on its own transport.
        """
        return self._async_transport or self._transport

    @property
    def has_async_transport(self) -> bool:
        """Whether a dedicated async transport was set via :meth:`with_async_transport`."""
        return self._async_transport is not None

    @property
    def rate_limiter(self) -> RateLimiter | None:
        """The shared rate limiter pacing this request's transport, if any."""
        return self._rate_limiter

    def with_transport(
        self,
        proxies: dict[str, str] | None = None,
        verify: bool | str | None = None,
        timeout: float | tuple[float, Optional[float]] | NoTimeoutType | None = None,
        session: requests.Session | None = None,
        *,
        pool_connections: int = DEFAULT_POOL_CONNECTIONS,
        pool_maxsize: int = DEFAULT_POOL_MAXSIZE,
        pool_block: bool = False,
    ) -> Self:
        """Configure the HTTP transport (proxy, SSL, timeout, custom session).

        All parameters are optional.  Per-request values (``request.proxies``,
        ``request.verify``) take precedence over transport-level values. A rate
        limiter configured with :meth:`with_rate_limit` is preserved.

        Args:
            proxies: Proxy URLs (e.g. ``{"https": "http://proxy:8080"}``)
            verify: SSL verification — ``True``, ``False``, or a CA bundle path.
                ``None`` (default) defers to the session/environment default.
            timeout: Request timeout — a number or a ``(connect, read)`` tuple.
                When ``None`` the bundled default (10 s connect, unbounded read)
                applies; pass
                :data:`~office365.runtime.transport.base.NO_TIMEOUT` to disable.
            session: Custom ``requests.Session`` with pre-configured adapters
            pool_connections: Host connection pools kept per session (ignored
                when ``session`` is supplied)
            pool_maxsize: Maximum connections per host pool (ignored when
                ``session`` is supplied)
            pool_block: Block when a pool is full instead of discarding the
                connection (ignored when ``session`` is supplied)

        Returns:
            Self: Supports method chaining
        """
        self._transport = RequestsTransport(
            session=session,
            proxies=proxies,
            verify=verify,
            timeout=timeout,
            pool_connections=pool_connections,
            pool_maxsize=pool_maxsize,
            pool_block=pool_block,
        )
        if self._rate_limiter is not None:
            self._transport = ThrottledTransport(self._transport, self._rate_limiter)
        return self

    def with_async_transport(self, transport: BaseTransport) -> Self:
        """Set the transport used by ``execute_query_async``.

        By default the async path offloads :attr:`transport` to a worker thread.
        Pass a native async transport (e.g. an httpx-backed one) to run async
        requests without worker threads, while the synchronous path keeps using
        :attr:`transport` unchanged.

        When a rate limiter is configured (see :meth:`with_rate_limit`) the
        dedicated async transport is wrapped so the async path is paced too.

        Args:
            transport: The transport to use for asynchronous execution.

        Returns:
            Self: Supports method chaining
        """
        self._async_transport = self._with_limiter(transport)
        return self

    def _with_limiter(self, transport: BaseTransport) -> BaseTransport:
        """Wrap ``transport`` in the shared limiter, unless none is configured.

        Unwraps an existing :class:`ThrottledTransport` first, so re-configuring
        replaces the limiter instead of stacking wrappers.
        """
        if self._rate_limiter is None:
            return transport
        inner = transport.inner if isinstance(transport, ThrottledTransport) else transport
        return ThrottledTransport(inner, self._rate_limiter)

    def with_rate_limit(
        self,
        health_threshold: int = 80,
        min_interval: float = 0.0,
        per_scope: bool = False,
    ) -> Self:
        """Pace every request of this request through a new shared rate limiter.

        Control plane: wraps the transport so the whole fleet — including the
        parallel batches dispatched by a context's ``execute_batch`` — is gated
        by ``Retry-After`` / ``X-SharePointHealthScore`` as a group. Unlike the
        ``after_execute`` observation hooks (``rate_limit_hook`` /
        ``throttle_guard``), this acts on the signals without affecting error
        propagation. Re-applying replaces the limiter (the underlying transport
        is not stacked).

        Args:
            health_threshold: Health score at/above which the group paces.
            min_interval: Minimum pause applied on a high health score (seconds).
            per_scope: When ``True``, a Graph ``x-ms-throttle-scope`` pauses only
                requests tagged with that same ``RequestOptions.throttle_scope``
                instead of the whole fleet.

        Returns:
            Self: Supports method chaining
        """
        return self.with_rate_limiter(
            RateLimiter(
                health_threshold=health_threshold,
                min_interval=min_interval,
                per_scope=per_scope,
            )
        )

    def with_rate_limiter(self, limiter: RateLimiter) -> Self:
        """Pace every request through a caller-provided shared rate limiter.

        Used to share one limiter across a fleet of contexts/clones (see
        :meth:`RateLimiter.bind`). Re-applying replaces the limiter without
        stacking wrappers.

        Args:
            limiter: The shared :class:`RateLimiter` gating the fleet.

        Returns:
            Self: Supports method chaining
        """
        self._rate_limiter = limiter
        self._transport = self._with_limiter(self._transport)
        if self._async_transport is not None:
            self._async_transport = self._with_limiter(self._async_transport)
        return self

    @property
    def client_request_id_enabled(self) -> bool:
        """Whether a unique ``client-request-id`` is sent with each request."""
        return self._client_request_id_enabled

    def with_client_request_id(self, enabled: bool = True) -> Self:
        """Enable or disable the per-request ``client-request-id`` header.

        When enabled (the default) every outgoing request — including each
        sub-request of a batch — carries a fresh GUID, matching the Microsoft
        Graph best practice for correlating a call with server-side logs. Pass
        ``False`` to opt out; a header set explicitly on a request always wins.

        Args:
            enabled: ``True`` to send the header (default), ``False`` to omit it.

        Returns:
            Self: Supports method chaining
        """
        self._client_request_id_enabled = enabled
        return self

    def apply_client_request_id(self, request: RequestOptions) -> None:
        """Ensure ``request`` carries a ``client-request-id`` correlation GUID.

        A no-op when disabled or when the caller already set the header. Called
        on both the direct send path and when building batch sub-requests so the
        whole fleet stays traceable.
        """
        if self._client_request_id_enabled:
            request.ensure_header("client-request-id", str(uuid.uuid4()))

    @property
    def auto_retry(self) -> bool:
        """Whether a client-level retry policy is active (see :meth:`with_auto_retry`)."""
        return self._retry_policy is not None

    @property
    def retry_policy(self) -> dict[str, Any] | None:
        """The active retry policy, or ``None`` when auto-retry is disabled."""
        return self._retry_policy

    def with_auto_retry(
        self,
        max_retry: int = 5,
        timeout_secs: int = 5,
        max_delay: Optional[int] = None,
        jitter: bool = True,
        exceptions: Tuple[Type[Exception], ...] = DEFAULT_RETRY_EXCEPTIONS,
        is_retriable: Optional[Callable[[Exception], bool]] = None,
    ) -> Self:
        """Enable client-level retry of transient failures (opt-in).

        A transport-level resilience setting, configured next to
        :meth:`with_rate_limit`; :meth:`~office365.runtime.client_runtime_context.ClientRuntimeContext.with_auto_retry`
        exposes the same method on the client facade.

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
        self._retry_policy = {
            "max_retry": max_retry,
            "timeout_secs": timeout_secs,
            "max_delay": max_delay,
            "jitter": jitter,
            "exceptions": exceptions,
            "is_retriable": is_retriable,
        }
        return self

    @property
    @abstractmethod
    def service_root_url(self) -> str:
        """Gets the service root URL."""

    @abstractmethod
    def build_request(self, query: ClientQuery) -> RequestOptions:
        """Transform query into request options

        Args:
            query: The client query to execute

        Returns:
            Configured RequestOptions object"""

    @abstractmethod
    def process_response(self, response: Response, query: ClientQuery) -> None:
        """Handle and transform the response

        Args:
            response: Raw HTTP response
            query: Original query that generated this response"""

    def execute_query(self, query: ClientQuery) -> None:
        """Submits a pending request to the server"""
        try:
            request = self.build_request(query)
            response = self.execute_request_direct(request)
            self.process_response(response, query)
            self.afterExecute(response)
        except ClientRequestException as e:
            self._add_permission_hint(e, query)
            if self._dispatch_error(e):
                return
            raise
        except HTTPError as e:
            exc = ClientRequestException.from_response(e.response)
            self._add_permission_hint(exc, query)
            raise exc from e

    def _dispatch_error(self, e: ClientRequestException) -> bool:
        """Notify error handlers and report whether one of them handled ``e``.

        A failure is swallowed only when a registered handler whose condition
        matched actually ran; stale scoped handlers no longer hide later,
        unrelated failures. See :meth:`on_error`.
        """
        if not self.onError:
            return False
        self._error_handled = False
        self.onError(e)
        return self._error_handled

    async def execute_query_async(self, query: ClientQuery) -> None:
        """Submits a pending request to the server without blocking the loop.

        Async counterpart of :meth:`execute_query` with the same semantics:
        ``beforeExecute`` runs before the request, and ``process_response`` /
        ``afterExecute`` run after the awaited response. Errors are dispatched to
        ``onError`` (swallowed) or re-raised, mirroring the sync path.
        """
        try:
            request = self.build_request(query)
            response = await self.execute_request_direct_async(request)
            self.process_response(response, query)
            self.afterExecute(response)
        except ClientRequestException as e:
            self._add_permission_hint(e, query)
            if self._dispatch_error(e):
                return
            raise
        except HTTPError as e:
            exc = ClientRequestException.from_response(e.response)
            self._add_permission_hint(exc, query)
            raise exc from e

    @staticmethod
    def _add_permission_hint(exc: ClientRequestException, query: ClientQuery) -> None:
        """Enrich a denied request with the permission the called API declares.

        The declaration comes from ``@require_permission``, which tags the query
        it built (``query.permission_requirement``). Only permission denials are
        enriched, so the hint cannot mislead on an unrelated failure.
        """
        from office365.runtime.exceptions import AccessDeniedException

        if not isinstance(exc, AccessDeniedException):
            return
        requirement = getattr(query, "permission_requirement", None)
        to_hint = getattr(requirement, "to_hint", None)
        if callable(to_hint):
            hint = to_hint()
            if isinstance(hint, str) and hint:
                exc.add_hint(hint)

    def on_error(
        self,
        action: Callable[[ClientRequestException], None],
        once: bool = True,
        condition: Optional[Callable[[], bool]] = None,
    ) -> Self:
        """Register a handler that **handles** (and therefore swallows) an error.

        When a query fails and at least one registered handler's ``condition``
        matches, the error is dispatched to that handler and :meth:`execute_query`
        does not re-raise — this powers the library's create-if-not-exists flows.
        If no registered handler matches, the failure is re-raised, so a stale
        scoped handler can never hide an unrelated later error. It is a control
        hook, not an observation hook: do not attach a limiter or a pure reporter
        here, or request failures will be silently suppressed (breaking retries).
        Use ``after_execute`` / ``throttle_guard`` for observation.

        Args:
            action: Callback receiving the error.
            once: Remove the handler after it fires (default True).
            condition: Optional predicate; when it returns False the handler is
                skipped and does **not** swallow the error.
        """

        def _process_error(e: ClientRequestException):
            matches = condition is None or condition()
            if matches:
                if once:
                    self.onError -= _process_error
                self._error_handled = True
                action(e)

        self.onError += _process_error
        return self

    def before_execute(
        self,
        action: Callable[[RequestOptions], None],
        once: bool = True,
        condition: Optional[Callable[[], bool]] = None,
    ) -> Self:
        """Attaches pre-query execution handler.

        Args:
            action: Callback to execute before query
            once: Whether to execute only once
            condition: Optional condition to check before executing action

        Returns:
            Self for method chaining
        """

        def _process_request(request: RequestOptions):
            if condition is None or condition():
                if once:
                    self.beforeExecute -= _process_request
                action(request)

        self.beforeExecute += _process_request
        return self

    def after_execute(
        self,
        action: Callable[[Response], Any],
        once: bool = True,
        condition: Optional[Callable[[], bool]] = None,
    ) -> Self:
        """Attaches post-execution handler for all requests.

        Args:
            action: Callback to execute after request
            once: Whether to execute only once
            condition: Optional condition to check before executing action

        Returns:
            Self for method chaining
        """

        def _process_response(response: Response) -> None:
            if condition is None or condition():
                if once:
                    self.afterExecute -= _process_response
                action(response)

        self.afterExecute += _process_response
        return self

    @staticmethod
    def _raise_for_status(response: Response) -> None:
        """Check HTTP status and dispatch to the right exception type via the factory."""
        try:
            response.raise_for_status()
        except HTTPError:
            raise ClientRequestException.from_response(response) from None

    def _observe_throttle(self, response: Optional[Response]) -> None:
        """Feed a sub-response into the transport's shared rate limiter, if any.

        Batch responses carry per-sub-request throttling signals that the
        transport (which only sees the outer ``200``) cannot observe, so the
        batch loop surfaces each sub-response here.
        """
        limiter = self._rate_limiter
        if limiter is None:
            limiter = getattr(self._transport, "limiter", None)
        if limiter is not None:
            limiter.observe(response)

    def execute_request_direct(self, request: RequestOptions) -> Response:
        """Execute the client request"""
        self.beforeExecute(request)
        self.apply_client_request_id(request)
        response = self._transport.execute(request)
        self._raise_for_status(response)
        return response

    async def before_execute_async(self, request: RequestOptions) -> None:
        """Run ``beforeExecute`` hooks without blocking the event loop.

        Auth, form-digest refresh and user hooks are synchronous callbacks that
        may perform blocking I/O (e.g. a token refresh). Like
        :meth:`~office365.runtime.transport.base.BaseTransport.execute_async`
        does for the request itself, they are offloaded to a worker thread so a
        slow hook cannot stall the loop. Handlers registered ``once`` still run
        exactly once and registration order is preserved.

        When an awaitable auth hook was registered (``_async_authenticate`` —
        used by async token callbacks), it is awaited on the loop first, so the
        token can be fetched with genuinely asynchronous I/O. The synchronous
        auth hook that follows then finds the request already authenticated.

        Args:
            request: The request about to be sent.
        """
        if self._async_authenticate is not None:
            await self._async_authenticate(request)
        await run_offloaded(self.beforeExecute, request)

    async def execute_request_direct_async(self, request: RequestOptions) -> Response:
        """Execute the client request without blocking the loop.

        Mirrors :meth:`execute_request_direct` but awaits the transport's
        :meth:`~office365.runtime.transport.base.BaseTransport.execute_async`.
        """
        await self.before_execute_async(request)
        self.apply_client_request_id(request)
        response = await self.async_transport.execute_async(request)
        self._raise_for_status(response)
        return response

    def execute_request(self, path: str) -> Response:
        """Executes request directly against the specified path.

        Args:
            path: The URL path to request

        Returns:
            Raw response from server
        """
        full_url = "".join([self.service_root_url, "/", path])
        request = RequestOptions(url=full_url)
        return self.execute_request_direct(request)

    async def execute_request_async(self, path: str) -> Response:
        """Executes request directly against the specified path, without blocking the loop.

        Async counterpart of :meth:`execute_request`; awaits
        :meth:`execute_request_direct_async`.

        Args:
            path: The URL path to request

        Returns:
            Raw response from server
        """
        full_url = "".join([self.service_root_url, "/", path])
        request = RequestOptions(url=full_url)
        return await self.execute_request_direct_async(request)
