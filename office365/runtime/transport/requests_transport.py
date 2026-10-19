"""Default HTTP transport backed by ``requests.Session``."""

from __future__ import annotations

import threading
from typing import Any, Optional, Tuple

from requests import Response, Session
from requests.adapters import HTTPAdapter

from office365.runtime.http.request_options import RequestOptions
from office365.runtime.transport.base import (
    DEFAULT_CONNECT_TIMEOUT,
    DEFAULT_READ_TIMEOUT,
    BaseTransport,
    NoTimeoutType,
    TimeoutValue,
)

#: Default timeout applied when none is configured: bounds the connect phase
#: (10 s) and the read phase (300 s). A server that stops responding therefore
#: fails after the read timeout instead of blocking the caller forever, while a
#: long upload/download that keeps moving is unaffected. ``requests`` has no
#: separate write timeout, so a stalled body is covered by the read value. Pass
#: :data:`~office365.runtime.transport.base.NO_TIMEOUT` to disable it.
DEFAULT_TIMEOUT: Optional[Tuple[float, Optional[float]]] = (DEFAULT_CONNECT_TIMEOUT, DEFAULT_READ_TIMEOUT)

#: Default number of host connection pools kept per session (``HTTPAdapter``).
DEFAULT_POOL_CONNECTIONS = 10

#: Default maximum connections kept per host pool (``HTTPAdapter``).
DEFAULT_POOL_MAXSIZE = 10


class RequestsTransport(BaseTransport):
    """HTTP transport using ``requests.Session`` for connection reuse.

    Thread safety:
        ``requests.Session`` is not safe to share across threads, so by default
        the transport keeps one lazily-created session *per thread* (each with
        its own connection pool and cookie jar). This makes the default
        transport safe under the parallel/offloaded requests the async runtime
        dispatches, without any opt-in.

        When the caller supplies an explicit ``session`` (for custom adapters,
        TLS config or session-level auth), that *single* session is used as-is
        and its thread safety becomes the caller's responsibility — pass a
        session whose adapter is safe for concurrent use if you also call the
        async/parallel APIs.

    Connection pooling:
        Each lazily-created per-thread session is fitted with an
        :class:`~requests.adapters.HTTPAdapter` sized by ``pool_connections`` /
        ``pool_maxsize`` / ``pool_block``. Raise ``pool_maxsize`` when many
        requests to one host run concurrently; the defaults match
        ``requests``. These settings are ignored when an explicit ``session``
        is supplied, since that session's adapters are the caller's.

    Args:
        session: Optional external ``Session`` for custom adapters or TLS config.
            When omitted, a session is created per thread on demand.
        proxies: Transport-level proxy configuration applied to all requests
        verify: SSL verification (``True``, ``False``, or a CA bundle path).
            ``None`` (the default) leaves the session/environment value in place,
            so a custom CA bundle set on a supplied ``session`` is honored.
            A per-request ``verify`` always wins.
        timeout: Request timeout — a number or a ``(connect, read)`` tuple. When
            ``None`` the :data:`DEFAULT_TIMEOUT` (10 s connect, 300 s read)
            applies; pass ``NO_TIMEOUT`` to disable timeouts entirely.
        pool_connections: Number of host connection pools kept per session.
        pool_maxsize: Maximum connections kept per host pool.
        pool_block: Whether to block waiting for a free connection instead of
            discarding it when a pool is full.
    """

    def __init__(
        self,
        session: Session | None = None,
        proxies: dict[str, str] | None = None,
        verify: bool | str | None = None,
        timeout: TimeoutValue | NoTimeoutType | None = None,
        *,
        pool_connections: int = DEFAULT_POOL_CONNECTIONS,
        pool_maxsize: int = DEFAULT_POOL_MAXSIZE,
        pool_block: bool = False,
    ) -> None:
        if pool_connections < 1:
            raise ValueError("pool_connections must be a positive integer")
        if pool_maxsize < 1:
            raise ValueError("pool_maxsize must be a positive integer")
        self._proxies = proxies
        self._verify = verify
        self._timeout = self._resolve_timeout(timeout)
        self._pool_connections = pool_connections
        self._pool_maxsize = pool_maxsize
        self._pool_block = pool_block
        # A caller-supplied session is shared verbatim across threads; otherwise
        # one session is created per thread on first use.
        self._explicit_session = session
        self._thread_local: threading.local | None = None if session is not None else threading.local()
        self._sessions: list[Session] = []
        self._sessions_lock = threading.Lock()
        if session is not None:
            self._sessions.append(session)

    def _create_session(self) -> Session:
        """Create and track a new session for the calling thread."""
        session = Session()
        adapter = HTTPAdapter(
            pool_connections=self._pool_connections,
            pool_maxsize=self._pool_maxsize,
            pool_block=self._pool_block,
        )
        session.mount("https://", adapter)
        session.mount("http://", adapter)
        with self._sessions_lock:
            self._sessions.append(session)
        return session

    def _current_session(self) -> Session:
        """Return the session bound to the calling thread, creating it on demand."""
        if self._explicit_session is not None:
            return self._explicit_session
        assert self._thread_local is not None
        session = getattr(self._thread_local, "session", None)
        if session is None:
            session = self._create_session()
            self._thread_local.session = session
        return session

    @staticmethod
    def _resolve_timeout(timeout: TimeoutValue | NoTimeoutType | None) -> Optional[TimeoutValue]:
        if timeout is None:
            return DEFAULT_TIMEOUT
        if isinstance(timeout, NoTimeoutType):
            return None
        return timeout

    @property
    def proxies(self) -> dict[str, str] | None:
        return self._proxies

    @property
    def verify(self) -> bool | str | None:
        return self._verify

    @property
    def timeout(self) -> Optional[TimeoutValue]:
        return self._timeout

    @property
    def pool_connections(self) -> int:
        """Number of host connection pools kept per session."""
        return self._pool_connections

    @property
    def pool_maxsize(self) -> int:
        """Maximum connections kept per host pool."""
        return self._pool_maxsize

    @property
    def pool_block(self) -> bool:
        """Whether a full pool blocks instead of discarding a connection."""
        return self._pool_block

    @property
    def auth(self) -> Any | None:
        if self._explicit_session is not None:
            return self._explicit_session.auth
        assert self._thread_local is not None
        session = getattr(self._thread_local, "session", None)
        return session.auth if session is not None else None

    def execute(self, request: RequestOptions) -> Response:
        kwargs: dict[str, Any] = {"headers": request.headers}
        # A per-request value wins; otherwise fall back to the transport-level
        # one; when neither is set the ``requests`` session/environment default
        # applies (so a custom CA bundle on the session is preserved).
        verify = request.verify if request.verify is not None else self._verify
        if verify is not None:
            kwargs["verify"] = verify
        proxies = request.proxies if request.proxies is not None else self._proxies
        if proxies is not None:
            kwargs["proxies"] = proxies
        if request.auth is not None:
            kwargs["auth"] = request.auth
        # A per-request timeout wins over the transport-level one; both accept a
        # single value or a ``(connect, read)`` tuple. When neither is set the
        # transport default (10 s connect, 300 s read) applies.
        timeout = request.timeout if request.timeout is not None else self._timeout
        if timeout is not None:
            kwargs["timeout"] = timeout

        method = request.method.value.lower()
        if method in ("post", "patch"):
            kwargs["data" if request.is_bytes or request.is_file else "json"] = request.data
        elif method == "put":
            kwargs["data"] = request.data
        elif method == "get":
            kwargs["stream"] = request.stream

        return getattr(self._current_session(), method)(request.url, **kwargs)

    def reset_connections(self) -> None:
        """Clear the calling thread's connection pool so the retry opens a new socket.

        ``Session.close()`` releases pooled (idle) connections while leaving the
        session usable, so the next request transparently builds a fresh pool.
        Only the current thread's session is reset: with thread-local sessions a
        retry on one worker must never close another worker's pool mid-flight.
        """
        self._current_session().close()

    def close(self) -> None:
        """Close every session this transport created, across all threads."""
        with self._sessions_lock:
            sessions = list(self._sessions)
        for session in sessions:
            session.close()
