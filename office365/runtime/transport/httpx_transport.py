"""Optional native-async HTTP transport backed by ``httpx`` (encode/httpx).

Unlike the default :class:`~office365.runtime.transport.base.BaseTransport`
implementation — which offloads the blocking ``requests`` call to a worker
thread — this transport performs genuinely asynchronous I/O on the event loop.

It is **optional**: install it with ``pip install
office365-rest-python-client[httpx]`` and opt in per request via
:meth:`~office365.runtime.client_request.ClientRequest.with_async_transport`::

    from office365.runtime.transport.httpx_transport import HttpxTransport

    ctx = ClientContext(site_url).with_credentials(credentials)
    ctx.pending_request().with_async_transport(HttpxTransport())
    await ctx.web.get().execute_query_async()

The synchronous path keeps using the default ``requests``-based transport, so
adding this does not change existing behaviour.

Notes:
    * Responses are adapted to :class:`requests.Response` so downstream
      processing is unchanged; the body is read eagerly, so ``stream=True``
      downloads (``response.iter_content``) work but are buffered in memory.
    * TLS verification, proxies and redirect policy are client-level
      (constructor) settings; per-request ``verify``/``proxies`` are not honored.
    * The transport may outlive an event loop: it rebuilds its own
      ``httpx.AsyncClient`` when it is used from a new loop, because a
      connection pool cannot follow a loop that has already finished. An
      ``async_client`` you inject is never replaced — its lifetime is yours.
"""

from __future__ import annotations

import asyncio
from typing import Any, AsyncIterator, Iterator, Optional

from requests import Response
from requests.exceptions import ConnectionError as RequestsConnectionError
from requests.exceptions import Timeout as RequestsTimeout
from requests.structures import CaseInsensitiveDict

from office365.runtime.http.request_options import RequestOptions
from office365.runtime.transport.base import (
    DEFAULT_CONNECT_TIMEOUT,
    DEFAULT_STREAM_CHUNK_SIZE,
    BaseTransport,
    HeadersCallback,
    NoTimeoutType,
)


class HttpxTransport(BaseTransport):
    """Native-async HTTP transport using ``httpx`` clients.

    Args:
        verify: TLS verification (``True``, ``False`` or a CA bundle path),
            applied to both clients.
        timeout: Default timeout — a number, an :class:`httpx.Timeout`, or
            ``None`` to use the bundled default (10 s connect, unbounded read).
            Pass :data:`~office365.runtime.transport.base.NO_TIMEOUT` to disable
            timeouts entirely. A per-request timeout overrides it.
        follow_redirects: Whether to follow redirects (default ``True`` to match
            ``requests``).
        client: Optional pre-built ``httpx.Client`` (mainly for tests).
        async_client: Optional pre-built ``httpx.AsyncClient`` (mainly for tests).
        **client_kwargs: Extra keyword arguments forwarded to both clients.
    """

    def __init__(
        self,
        *,
        verify: bool | str = True,
        timeout: Any | None = None,
        follow_redirects: bool = True,
        client: Any | None = None,
        async_client: Any | None = None,
        **client_kwargs: Any,
    ) -> None:
        try:
            import httpx
        except ImportError as exc:  # pragma: no cover - exercised only without the extra
            raise ImportError(
                "HttpxTransport requires httpx. Install it with 'pip install office365-rest-python-client[httpx]'."
            ) from exc

        self._httpx = httpx
        resolved_timeout = self._resolve_timeout(httpx, timeout)
        self._client = (
            client
            if client is not None
            else httpx.Client(
                verify=verify, timeout=resolved_timeout, follow_redirects=follow_redirects, **client_kwargs
            )
        )
        # Kept as a factory, not only as an instance: a pooled ``AsyncClient``
        # cannot be reused from a second event loop, so a stale one is replaced
        # with an identically configured one (see _async_client_for_running_loop).
        self._async_client_factory = lambda: httpx.AsyncClient(
            verify=verify, timeout=resolved_timeout, follow_redirects=follow_redirects, **client_kwargs
        )
        self._async_client_owned = async_client is None
        self._async_client = self._async_client_factory() if async_client is None else async_client
        self._async_loop: Any | None = None

    @staticmethod
    def _resolve_timeout(httpx: Any, timeout: Any | None) -> Any:
        """Map the public ``timeout`` to an ``httpx`` timeout value.

        ``None`` selects the bundled default (bounded connect, unbounded read),
        :data:`NO_TIMEOUT` disables timeouts, and anything else (a number or an
        ``httpx.Timeout``) is forwarded unchanged.
        """
        if timeout is None:
            return httpx.Timeout(connect=DEFAULT_CONNECT_TIMEOUT, read=None, write=None, pool=None)
        if isinstance(timeout, NoTimeoutType):
            return None
        return timeout

    def execute(self, request: RequestOptions) -> Response:
        """Send a request synchronously through an ``httpx.Client``."""
        try:
            httpx_response = self._client.request(request.method.value, request.url, **self._build_kwargs(request))
        except self._httpx.TimeoutException as exc:
            raise RequestsTimeout(str(exc)) from exc
        except self._httpx.TransportError as exc:
            raise RequestsConnectionError(str(exc)) from exc
        return self._to_requests_response(httpx_response)

    def _async_client_for_running_loop(self) -> Any:
        """Return the async client bound to the loop that is running now.

        An ``httpx.AsyncClient`` holds its connection pool on the loop that
        created the connections, so reusing one instance across two
        ``asyncio.run()`` calls fails on the second with ``Event loop is
        closed``. A transport that outlives a loop — a script run twice, a
        notebook cell, a worker that builds a loop per request — therefore gets
        a fresh client for the new loop with the constructor settings intact.
        Closing the abandoned pool needs its (finished) loop, so it is released
        with the client. An injected client is never replaced.
        """
        loop = asyncio.get_running_loop()
        if self._async_loop is not loop:
            if self._async_loop is not None and self._async_client_owned:
                self._async_client = self._async_client_factory()
            self._async_loop = loop
        return self._async_client

    async def execute_async(self, request: RequestOptions) -> Response:
        """Send a request asynchronously through an ``httpx.AsyncClient``."""
        try:
            httpx_response = await self._async_client_for_running_loop().request(
                request.method.value, request.url, **self._build_kwargs(request)
            )
        except self._httpx.TimeoutException as exc:
            raise RequestsTimeout(str(exc)) from exc
        except self._httpx.TransportError as exc:
            raise RequestsConnectionError(str(exc)) from exc
        return self._to_requests_response(httpx_response)

    def stream(
        self,
        request: RequestOptions,
        chunk_size: int = DEFAULT_STREAM_CHUNK_SIZE,
        on_headers: Optional[HeadersCallback] = None,
    ) -> Iterator[bytes]:
        """Stream a response body synchronously through an ``httpx.Client``."""
        try:
            with self._client.stream(request.method.value, request.url, **self._build_kwargs(request)) as response:
                if response.status_code >= 400:  # noqa: PLR2004
                    self._to_error_response(response, response.read()).raise_for_status()
                if on_headers is not None:
                    on_headers(response.headers)
                yield from response.iter_bytes(chunk_size=chunk_size)
        except self._httpx.TimeoutException as exc:
            raise RequestsTimeout(str(exc)) from exc
        except self._httpx.TransportError as exc:
            raise RequestsConnectionError(str(exc)) from exc

    async def stream_async(
        self,
        request: RequestOptions,
        chunk_size: int = DEFAULT_STREAM_CHUNK_SIZE,
        on_headers: Optional[HeadersCallback] = None,
    ) -> AsyncIterator[bytes]:
        """Stream a response body natively on the event loop via ``httpx``."""
        try:
            async with self._async_client_for_running_loop().stream(
                request.method.value, request.url, **self._build_kwargs(request)
            ) as response:
                if response.status_code >= 400:  # noqa: PLR2004
                    self._to_error_response(response, await response.aread()).raise_for_status()
                if on_headers is not None:
                    on_headers(response.headers)
                async for chunk in response.aiter_bytes(chunk_size=chunk_size):
                    yield chunk
        except self._httpx.TimeoutException as exc:
            raise RequestsTimeout(str(exc)) from exc
        except self._httpx.TransportError as exc:
            raise RequestsConnectionError(str(exc)) from exc

    def close(self) -> None:
        """Close the synchronous client."""
        self._client.close()

    async def aclose(self) -> None:
        """Close both clients (the async one is awaited)."""
        await self._async_client_for_running_loop().aclose()
        self._client.close()

    def _build_kwargs(self, request: RequestOptions) -> dict[str, Any]:
        kwargs: dict[str, Any] = {"headers": request.headers}
        if request.auth is not None:
            kwargs["auth"] = request.auth
        if request.timeout is not None:
            # Translate the ``NO_TIMEOUT`` sentinel to httpx's "no timeout";
            # numbers and ``(connect, read[, write[, pool]])`` tuples are already
            # accepted verbatim by httpx.
            kwargs["timeout"] = None if isinstance(request.timeout, NoTimeoutType) else request.timeout

        method = request.method.value.lower()
        if method in ("post", "patch"):
            if request.data is not None:
                kwargs["content" if request.is_bytes or request.is_file else "json"] = request.data
        elif method == "put" and request.data is not None:
            kwargs["content"] = request.data
        return kwargs

    @staticmethod
    def _to_error_response(httpx_response: Any, content: bytes) -> Response:
        """Materialise an error ``httpx.Response`` as a ``requests.Response``.

        The body is read (the caller has already done so) so
        :meth:`~office365.runtime.client_request_exception.ClientRequestException.from_response`
        can parse the error payload.
        """
        response = Response()
        response.status_code = httpx_response.status_code
        response.reason = httpx_response.reason_phrase
        response.url = str(httpx_response.url)
        response.headers = CaseInsensitiveDict(httpx_response.headers)
        response._content = content
        response._content_consumed = True  # type: ignore[reportAttributeAccessIssue]
        return response

    @staticmethod
    def _to_requests_response(httpx_response: Any) -> Response:
        """Adapt an ``httpx.Response`` to a ``requests.Response``.

        The body is materialised so ``content``/``json``/``iter_content`` behave
        exactly as on a ``requests`` response.
        """
        response = Response()
        response.status_code = httpx_response.status_code
        response.reason = httpx_response.reason_phrase
        response.url = str(httpx_response.url)
        response.headers = CaseInsensitiveDict(httpx_response.headers)
        if httpx_response.encoding is None:
            response.encoding = httpx_response.charset_encoding
        else:
            response.encoding = httpx_response.encoding
        response._content = httpx_response.content
        response._content_consumed = True  # type: ignore[reportAttributeAccessIssue]
        return response
