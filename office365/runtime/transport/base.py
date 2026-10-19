"""Pluggable HTTP transport for the API client."""

from __future__ import annotations

from abc import ABC, abstractmethod
from concurrent.futures import Executor
from typing import Any, AsyncIterator, Callable, Iterator, Mapping, Optional, Tuple, Union

from requests import Response
from typing_extensions import Self

from office365.runtime.http.request_options import RequestOptions
from office365.runtime.transport.offload import get_offload_executor, run_offloaded

#: Default slice size (bytes) used by the streaming helpers.
DEFAULT_STREAM_CHUNK_SIZE = 8192

#: Default connect timeout (seconds) used by the bundled transports: bounds
#: connection establishment.
DEFAULT_CONNECT_TIMEOUT = 10.0

#: Default read timeout (seconds): bounds the wait for the next byte from the
#: server. A connection that stops responding therefore fails in minutes instead
#: of blocking the caller forever, while a long transfer that keeps trickling is
#: unaffected — the clock restarts on every byte, so this is a gap bound, not a
#: total-transfer bound. Raise it per request or per transport; pass
#: :data:`NO_TIMEOUT` to remove it.
DEFAULT_READ_TIMEOUT = 300.0

#: Default write timeout (seconds) for transports that distinguish it (httpx):
#: bounds the wait for the socket to accept the next chunk of a request body.
DEFAULT_WRITE_TIMEOUT = 300.0

#: Default pool timeout (seconds) for transports that distinguish it (httpx):
#: bounds the wait for a free connection from the connection pool.
DEFAULT_POOL_TIMEOUT = 10.0

HeadersCallback = Callable[[Mapping[str, str]], None]


class NoTimeoutType:
    """Sentinel type for :data:`NO_TIMEOUT`."""

    __slots__ = ()

    def __repr__(self) -> str:
        return "NO_TIMEOUT"


#: Pass as ``timeout`` to a bundled transport to disable its default timeout.
NO_TIMEOUT = NoTimeoutType()

#: A transport-level timeout: a single number or a ``(connect, read)`` tuple.
TimeoutValue = Union[float, Tuple[float, Optional[float]]]


class BaseTransport(ABC):
    """Abstract HTTP transport layer.

    Implementations handle the actual HTTP request/response cycle.
    The default implementation uses ``requests.Session``.

    Every transport is usable in both synchronous (:meth:`execute`) and
    asynchronous (:meth:`execute_async`) code. The async path defaults to
    offloading :meth:`execute` to a worker thread, so a transport backed by a
    blocking client (e.g. ``requests``) needs no async-specific code.
    """

    #: Optional worker pool for the async offload path. ``None`` (the default)
    #: uses the process-wide pool from
    #: :func:`office365.runtime.transport.offload.get_offload_executor`, which
    #: :func:`...configure_offload_executor` can size. Set it to give this
    #: transport its own executor; the executor must outlive the transport.
    offload_executor: Optional[Executor] = None

    def _get_offload_executor(self) -> Executor:
        """Return the executor backing the default async offload path."""
        return self.offload_executor or get_offload_executor()

    @abstractmethod
    def execute(self, request: RequestOptions) -> Response:
        """Send an HTTP request and return the response."""

    async def execute_async(self, request: RequestOptions) -> Response:
        """Send an HTTP request and return the response, without blocking the loop.

        The default implementation runs the blocking :meth:`execute` in a worker
        thread, so every transport becomes awaitable as-is and the underlying
        session (auth, proxies, connection reuse, rate limiting) is shared with
        the synchronous path.

        Transports with a native async engine override this method.

        Args:
            request: The request to send.

        Returns:
            The HTTP response.
        """
        return await run_offloaded(self.execute, request, executor=self._get_offload_executor())

    def stream(
        self,
        request: RequestOptions,
        chunk_size: int = DEFAULT_STREAM_CHUNK_SIZE,
        on_headers: Optional[HeadersCallback] = None,
    ) -> Iterator[bytes]:
        """Send a request and yield the response body incrementally.

        The default implementation sets ``request.stream``, delegates the send to
        :meth:`execute` — so auth, pacing, proxies and connection reuse are
        unchanged — and iterates the body in ``chunk_size`` slices. The response
        is closed when iteration finishes, the caller stops early, or an error
        occurs.

        Args:
            request: The request to send.
            chunk_size: Number of bytes per chunk.
            on_headers: Optional callback invoked once with the response headers
                before the first chunk (e.g. to read ``Content-Length``).

        Yields:
            The response body in ``chunk_size`` slices.

        Raises:
            requests.HTTPError: When the server returns an error status.
        """
        request.stream = True
        response = self.execute(request)
        try:
            response.raise_for_status()
            if on_headers is not None:
                on_headers(response.headers)
            yield from response.iter_content(chunk_size=chunk_size)
        finally:
            response.close()

    async def stream_async(
        self,
        request: RequestOptions,
        chunk_size: int = DEFAULT_STREAM_CHUNK_SIZE,
        on_headers: Optional[HeadersCallback] = None,
    ) -> AsyncIterator[bytes]:
        """Async twin of :meth:`stream` that never blocks the event loop.

        Transports with a native async streaming engine override this. The
        default implementation drives the blocking :meth:`stream` in a worker
        thread one chunk per wait, so the loop stays free while a
        ``requests``-backed response body is read.

        Args:
            request: The request to send.
            chunk_size: Number of bytes per chunk.
            on_headers: Optional callback invoked once with the response headers
                before the first chunk.

        Yields:
            The response body in ``chunk_size`` slices.
        """
        iterator = self.stream(request, chunk_size=chunk_size, on_headers=on_headers)

        def _next_chunk() -> Optional[bytes]:
            try:
                return next(iterator)
            except StopIteration:
                return None

        try:
            while True:
                chunk = await run_offloaded(_next_chunk, executor=self._get_offload_executor())
                if chunk is None:
                    break
                yield chunk
        finally:
            close = getattr(iterator, "close", None)
            if close is not None:
                await run_offloaded(close, executor=self._get_offload_executor())

    @property
    def proxies(self) -> dict[str, str] | None:
        """Transport-level proxy configuration."""
        return None

    @property
    def verify(self) -> bool | str | None:
        """Transport-level SSL verification (``None`` defers to the session)."""
        return True

    @property
    def timeout(self) -> Optional[TimeoutValue]:
        """Transport-level request timeout in seconds."""
        return None

    @property
    def auth(self) -> Any | None:
        """Transport-level authentication handler, e.g. ``session.auth``."""
        return None

    def reset_connections(self) -> None:  # noqa: B027
        """Discard pooled connections so the next request opens a fresh one.

        Called before retrying a ``502``/``503``/``504`` or connection failure so
        a poisoned keep-alive socket is not reused (Microsoft Graph best
        practices). The default is a no-op; transports that pool connections
        override it.
        """

    def close(self) -> None:  # noqa: B027
        """Release transport resources (connections, etc.)."""

    async def aclose(self) -> None:
        """Asynchronously release transport resources.

        Default: run the synchronous :meth:`close` in a worker thread. Native
        async transports override this to await their own shutdown.
        """
        await run_offloaded(self.close, executor=self._get_offload_executor())

    def __enter__(self) -> Self:
        return self

    def __exit__(self, *args: object) -> None:
        self.close()
