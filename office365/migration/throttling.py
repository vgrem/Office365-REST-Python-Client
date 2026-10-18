"""Measure throttling during a migration run.

A migration is paced by the service, not only by its own tuning knobs: SharePoint
Online and Microsoft Graph answer an over-eager client with ``429 Too Many
Requests`` / ``503 Service Unavailable`` plus a ``Retry-After``, and the runtime
retries those transparently. That is the right behaviour, but it hides the cost —
a run that is being throttled on every batch reports the *throttled* throughput as
if it were the achievable one, so "is concurrency 8 faster than 4?" cannot be
answered and a pacing knob cannot be tuned.

:class:`ThrottleMonitor` closes that gap with one counter and no policy: it wraps a
context's transport (sync and async) and records responses, throttled responses by
status code, and the ``Retry-After`` seconds the server asked for. It never changes
control flow — retry, backoff and pacing stay where they are — so attaching one is
always safe.

Usage:
    >>> from office365.migration import ThrottleMonitor
    >>> monitor = ThrottleMonitor().attach(target_ctx).attach(source_ctx)
    >>> session = MigrationSession(throttle=monitor).register(context=target_ctx)
    >>> session.start()
    >>> print(monitor.summary())  # "throttled 3/171 response(s) (429: 2, 503: 1), 42s of Retry-After"

Contexts cloned from a monitored context (``ClientContext.clone``, used by the
whole-site resolver for every web) share its transport, so a web tree needs one
attach. A ``429``/``503`` is counted whether or not it carried headers, because the
status alone is the signal.
"""

from __future__ import annotations

import threading
from typing import TYPE_CHECKING, Any, Dict, Optional

from office365.runtime.retry import response_retry_after
from office365.runtime.transport.base import BaseTransport

if TYPE_CHECKING:
    from requests import Response

    from office365.runtime.client_runtime_context import ClientRuntimeContext
    from office365.runtime.http.request_options import RequestOptions

#: Statuses that mean "the service is asking the client to slow down".
THROTTLED_STATUS_CODES = frozenset({429, 503})


class _CountingTransport(BaseTransport):
    """Count throttled responses on a wrapped transport without affecting it."""

    def __init__(self, inner: BaseTransport, monitor: "ThrottleMonitor") -> None:
        self._inner = inner
        self._monitor = monitor

    @property
    def inner(self) -> BaseTransport:
        """The wrapped transport."""
        return self._inner

    @property
    def monitor(self) -> "ThrottleMonitor":
        """The monitor counting this transport's responses."""
        return self._monitor

    def execute(self, request: "RequestOptions") -> "Response":
        response = self._inner.execute(request)
        self._monitor.observe(response)
        return response

    async def execute_async(self, request: "RequestOptions") -> "Response":
        response = await self._inner.execute_async(request)
        self._monitor.observe(response)
        return response

    # The remaining transport surface (proxies, timeouts, auth, connection reuse)
    # belongs to the wrapped transport — this decorator only observes.
    @property
    def proxies(self) -> dict[str, str] | None:
        return self._inner.proxies

    @property
    def verify(self) -> bool | str | None:
        return self._inner.verify

    @property
    def timeout(self) -> Any:
        return self._inner.timeout

    @property
    def auth(self) -> Any:
        return self._inner.auth

    def reset_connections(self) -> None:
        self._inner.reset_connections()

    def close(self) -> None:
        self._inner.close()

    async def aclose(self) -> None:
        await self._inner.aclose()


class ThrottleMonitor:
    """A thread-safe tally of the responses a run sent and the ones it was throttled on.

    Observation only: it counts, it never retries, paces or fails. The counters are
    a denominator (all responses) and a numerator (``429``/``503``), plus the
    ``Retry-After`` seconds the service asked for — which is the additive cost
    throttling added to a run.
    """

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._responses = 0
        self._throttled = 0
        self._retry_after = 0.0
        self._by_status: Dict[int, int] = {}

    # ── Wiring ───────────────────────────────────────────────────

    def attach(self, context: "ClientRuntimeContext") -> "ThrottleMonitor":
        """Count every response sent through ``context``'s transports.

        Wraps the pending request's transport, and the dedicated async transport
        when one was configured (``with_async_transport``). Re-attaching replaces
        the wrapper rather than stacking a second one, and a context cloned
        afterwards (``ClientContext.clone``) shares the wrapped transport.

        Args:
            context: The client context to observe.

        Returns:
            Self: supports chaining (``ThrottleMonitor().attach(a).attach(b)``).
        """
        request = context.pending_request()
        request.transport = self._wrap(request.transport)
        if request.has_async_transport:
            request.with_async_transport(self._wrap(request.async_transport))
        return self

    def _wrap(self, transport: BaseTransport) -> BaseTransport:
        """Wrap ``transport`` in this monitor, unwrapping a previous wrapper."""
        inner = transport.inner if isinstance(transport, _CountingTransport) else transport
        return _CountingTransport(inner, self)

    # ── Sampling ─────────────────────────────────────────────────

    def observe(self, response: Optional["Response"]) -> None:
        """Count one response (thread-safe; called from the transport wrapper)."""
        status = getattr(response, "status_code", None)
        with self._lock:
            self._responses += 1
            if status not in THROTTLED_STATUS_CODES:
                return
            self._throttled += 1
            self._by_status[status] = self._by_status.get(status, 0) + 1
            delay = response_retry_after(response) if response is not None else None
            if delay:
                self._retry_after += float(delay)

    # ── Reading ──────────────────────────────────────────────────

    @property
    def responses(self) -> int:
        """How many responses the monitor has seen."""
        with self._lock:
            return self._responses

    @property
    def throttled(self) -> int:
        """How many of them were ``429``/``503``."""
        with self._lock:
            return self._throttled

    @property
    def retry_after(self) -> float:
        """Total ``Retry-After`` seconds the service asked the run to wait."""
        with self._lock:
            return self._retry_after

    def snapshot(self) -> dict:
        """The counters as a JSON-serializable dict (stable keys)."""
        with self._lock:
            return {
                "responses": self._responses,
                "throttled": self._throttled,
                "retry_after_s": round(self._retry_after, 3),
                "by_status": {str(code): count for code, count in sorted(self._by_status.items())},
            }

    def to_dict(self) -> dict:
        """Alias of :meth:`snapshot` for report/evidence-pack composition."""
        return self.snapshot()

    def summary(self) -> str:
        """One line a human or a log event can carry, or ``""`` when never throttled."""
        with self._lock:
            if not self._throttled:
                return ""
            codes = ", ".join(f"{code}: {count}" for code, count in sorted(self._by_status.items()))
            return (
                f"throttled {self._throttled}/{self._responses} response(s) ({codes}), "
                f"{self._retry_after:g}s of Retry-After"
            )

    def reset(self) -> None:
        """Clear the counters (used by tests and by a rerun of the same monitor)."""
        with self._lock:
            self._responses = 0
            self._throttled = 0
            self._retry_after = 0.0
            self._by_status.clear()


__all__ = ["THROTTLED_STATUS_CODES", "ThrottleMonitor"]
