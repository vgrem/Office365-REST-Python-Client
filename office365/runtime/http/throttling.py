"""Parsing and reacting to throttling / health signals on responses.

SharePoint Online reports server load via ``X-SharePointHealthScore`` on every
response and ``Retry-After`` on throttled (429/503) responses. Per the current
Microsoft guidance it does **not** return IETF ``RateLimit-*`` headers — those
are parsed defensively here in case a proxy or other source provides them.

Two distinct concerns live here:

**Control** — act on the signals to pace the fleet. :class:`RateLimiter` +
:func:`paced` (used by ``ThrottledTransport``) gate every send and observe every
response, including failures, without touching error propagation. This is the
mature pipeline/transport-policy pattern (Azure ``RetryPolicy``, botocore
adaptive mode, urllib3 ``Retry``).

**Observability** — report the signals to the caller. :func:`rate_limit_hook`
and :func:`throttle_guard` attach to the request's ``afterExecute`` event and
never change control flow. Use these when you only want to *know* about
throttling; use the limiter when you want to *act* on it.

Note: a request ``onError`` handler whose condition matches marks the error as
handled (it swallows it — see :meth:`ClientRequest.on_error`), so handlers must
not be used for observation.
"""

from __future__ import annotations

import asyncio
import threading
import time
from contextlib import contextmanager
from dataclasses import dataclass, fields
from enum import Enum
from typing import TYPE_CHECKING, Awaitable, Callable, Iterator, Optional

from requests import Response

from office365.runtime.converters.scalars import parse_int

if TYPE_CHECKING:
    from office365.runtime.client_runtime_context import ClientRuntimeContext


class ThrottleProtocol(Enum):
    """Which API's throttling headers to parse.

    ``AUTO`` (default) reads every known header — Microsoft Graph's
    ``x-ms-throttle-*`` / ``x-ms-resource-unit`` and SharePoint's
    ``X-SharePointHealthScore`` / ``RateLimit-*`` — so callers rarely need to
    pick one. The explicit values are an escape hatch for future quirks.
    """

    AUTO = "auto"
    GRAPH = "graph"
    SHAREPOINT = "sharepoint"


#: Fields that carry a server signal (``status`` is context, not a signal).
_SIGNAL_FIELDS = (
    "limit",
    "remaining",
    "reset",
    "retry_after",
    "health_score",
    "limit_percentage",
    "resource_unit",
    "scope",
    "reason",
)


@dataclass(frozen=True)
class ThrottleLimits:
    """Throttling state reported by the server, protocol-agnostic.

    Attributes:
        limit: Maximum requests permitted in the current window (IETF ``RateLimit-*``).
        remaining: Requests still permitted before throttling kicks in.
        reset: Seconds until the quota window resets.
        retry_after: Seconds the server asks us to wait (``Retry-After``).
        health_score: SharePoint health score (0-100), if reported.
        limit_percentage: Graph ``x-ms-throttle-limit-percentage`` (0.8-1.8) —
            how much of the granted limit the app consumed; >= 1.0 means requests
            are being throttled.
        resource_unit: Graph ``x-ms-resource-unit`` — the cost of this request.
        scope: Graph ``x-ms-throttle-scope`` — the throttled scope
            (``<Scope>/<Limit>/<AppId>/<TenantId|UserId|ResourceId>``).
        reason: Graph ``x-ms-throttle-information`` (``CPULimitExceeded``,
            ``WriteLimitExceeded``, ``ResourceUnitLimitExceeded``, ...).
        status: The HTTP status code.
    """

    limit: Optional[int] = None
    remaining: Optional[int] = None
    reset: Optional[int] = None
    retry_after: Optional[int] = None
    health_score: Optional[int] = None
    limit_percentage: Optional[float] = None
    resource_unit: Optional[int] = None
    scope: Optional[str] = None
    reason: Optional[str] = None
    status: Optional[int] = None

    @property
    def has_signals(self) -> bool:
        """Whether any throttling signal header was present."""
        return any(getattr(self, name) is not None for name in _SIGNAL_FIELDS)


#: Alias for the newer, protocol-agnostic name.
ThrottleSignal = ThrottleLimits

#: Cap on the ``x-ms-resource-unit`` cost multiplier so a single expensive
#: request can't translate into an unbounded pause.
MAX_RESOURCE_UNIT_COST = 10.0

_ALL_FIELDS = tuple(f.name for f in fields(ThrottleLimits))


def _parse_float(value: Optional[str]) -> Optional[float]:
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _parse_graph(response: Response) -> ThrottleLimits:
    """Parse Microsoft Graph throttling headers (``x-ms-throttle-*``)."""
    headers = response.headers
    return ThrottleLimits(
        retry_after=parse_int(headers.get("Retry-After")),
        limit_percentage=_parse_float(headers.get("x-ms-throttle-limit-percentage")),
        resource_unit=parse_int(headers.get("x-ms-resource-unit")),
        scope=headers.get("x-ms-throttle-scope"),
        reason=headers.get("x-ms-throttle-information"),
        status=getattr(response, "status_code", None),
    )


def _parse_sharepoint(response: Response) -> ThrottleLimits:
    """Parse SharePoint throttling/health headers."""
    headers = response.headers
    return ThrottleLimits(
        limit=parse_int(headers.get("RateLimit-Limit")),
        remaining=parse_int(headers.get("RateLimit-Remaining")),
        reset=parse_int(headers.get("RateLimit-Reset")),
        retry_after=parse_int(headers.get("Retry-After")),
        health_score=parse_int(headers.get("X-SharePointHealthScore")),
        status=getattr(response, "status_code", None),
    )


_PARSERS: dict[ThrottleProtocol, Callable[[Response], ThrottleLimits]] = {
    ThrottleProtocol.GRAPH: _parse_graph,
    ThrottleProtocol.SHAREPOINT: _parse_sharepoint,
}


def parse_throttling(
    response: Response,
    protocol: ThrottleProtocol = ThrottleProtocol.AUTO,
) -> Optional[ThrottleLimits]:
    """Parse throttling / health headers from a response into a ``ThrottleLimits``.

    Returns ``None`` when the response carries none of the tracked headers, so
    hooks can stay silent for ordinary responses. ``protocol=AUTO`` (default)
    reads every known header; pass an explicit protocol to restrict it.

    Args:
        response: The raw HTTP response.
        protocol: Which API's headers to read (default ``AUTO``).

    Returns:
        ThrottleLimits, or None when no tracked headers are present.
    """
    if protocol is ThrottleProtocol.AUTO:
        # ``Retry-After`` is common to both, so merge rather than short-circuit.
        graph = _parse_graph(response)
        sharepoint = _parse_sharepoint(response)
        limits = ThrottleLimits(
            **{
                name: (getattr(graph, name) if getattr(graph, name) is not None else getattr(sharepoint, name))
                for name in _ALL_FIELDS
            }
        )
    else:
        limits = _PARSERS[protocol](response)
    return limits if limits.has_signals else None


def rate_limit_hook(callback: Optional[Callable[[ThrottleLimits], None]] = None) -> Callable[[Response], None]:
    """Return an after-execute hook that reports parsed throttling / health state.

    Observation only — it never changes control flow (unlike :class:`RateLimiter`).
    The returned hook is compatible with ``after_execute`` (it expects the raw
    ``Response``). It fires ``callback`` only when the response carries any of
    the tracked headers — silent otherwise.

    Usage:
        >>> from office365.runtime.http.throttling import rate_limit_hook
        >>> items.get().after_execute(rate_limit_hook(my_callback), include_response=True).execute_query()
    """

    def _hook(response: Response) -> None:
        limits = parse_throttling(response)
        if limits is not None and callable(callback):
            callback(limits)

    return _hook


@contextmanager
def throttle_guard(
    context: "ClientRuntimeContext",
    on_limits: Optional[Callable[[ThrottleLimits], None]] = None,
) -> Iterator[None]:
    """Monitor throttling / health signals on every response within a scope.

    Attaches :func:`rate_limit_hook` to the request's ``afterExecute`` event
    handler on enter and removes it on exit, so the guard applies to every query
    executed inside the ``with`` block — no ``include_response`` plumbing needed.

    Args:
        context: The client context to monitor.
        on_limits: Optional callback invoked with parsed state per response
          (only when any of the tracked headers are present).

    Usage:
        >>> from office365.runtime.http.throttling import throttle_guard, ThrottleLimits
        >>> def pace(limits: ThrottleLimits) -> None:
        ...     if limits.remaining is not None and limits.remaining < 10:
        ...         time.sleep(limits.reset or 1)
        >>> with throttle_guard(ctx, on_limits=pace):
        ...     ctx.execute_query()
    """
    handler = context.pending_request().afterExecute
    hook = rate_limit_hook(on_limits)
    handler += hook
    try:
        yield
    finally:
        handler -= hook


@dataclass(frozen=True)
class PaceState:
    """The group gate: a monotonic deadline before which requests must wait.

    Produced only by :func:`pace` (pure) so the pacing policy is trivially
    testable without a clock, a lock, or a sleep.
    """

    next_available_at: float = 0.0


def pace(
    state: PaceState,
    limits: Optional[ThrottleLimits],
    *,
    now: float,
    health_threshold: int = 80,
    min_interval: float = 0.0,
    percentage_threshold: float = 0.8,
    percentage_interval: float = 1.0,
    weight_by_resource_unit: bool = True,
) -> PaceState:
    """Pure transition: observed server limits -> next gate state.

    A ``Retry-After`` gates the fleet for that long. A high Graph
    ``x-ms-throttle-limit-percentage`` (>= ``percentage_threshold``) applies a
    short, scaled pace so the group eases off *before* being throttled; a high
    ``X-SharePointHealthScore`` does the same as the farm heats up. Returns
    ``state`` unchanged when nothing applies.

    When ``weight_by_resource_unit`` is set and the response reports an
    ``x-ms-resource-unit`` cost, the proactive percentage pace is multiplied by
    that cost (capped at :data:`MAX_RESOURCE_UNIT_COST`) — an expensive call
    consumes more of the budget, so the group rests proportionally longer.
    ``Retry-After`` is the server's explicit instruction and is never scaled.

    Args:
        state: The current gate state.
        limits: Parsed throttling/health signals (or ``None``).
        now: Monotonic "now" (injected — the function reads no clock).
        health_threshold: Health score at/above which the group paces.
        min_interval: Minimum pause applied on a high health score.
        percentage_threshold: Graph limit-percentage at/above which the group paces.
        percentage_interval: Base pause for the Graph limit-percentage pace
            (scales 1x..2x across 0.8..1.8).
        weight_by_resource_unit: Scale the percentage pace by the request cost.
    """
    if limits is None:
        return state
    delay = 0.0
    if limits.retry_after is not None and limits.retry_after > 0:
        delay = max(delay, float(limits.retry_after))
    cost = 1.0
    if weight_by_resource_unit and limits.resource_unit is not None:
        cost = min(max(float(limits.resource_unit), 1.0), MAX_RESOURCE_UNIT_COST)
    if limits.limit_percentage is not None and limits.limit_percentage >= percentage_threshold:
        delay = max(delay, percentage_interval * (1.0 + (limits.limit_percentage - percentage_threshold)) * cost)
    if limits.health_score is not None and limits.health_score >= health_threshold:
        delay = max(delay, (limits.health_score - health_threshold) / 20.0, min_interval)
    if delay <= 0:
        return state
    return PaceState(max(state.next_available_at, now + delay))


def wait_delay(state: PaceState, *, now: float) -> float:
    """Pure: seconds until the gate opens (``0`` when already open)."""
    return max(0.0, state.next_available_at - now)


def paced(func: Callable[[], Response], gate: "RateLimiter", scope: Optional[str] = None) -> Response:
    """Run ``func`` under a shared rate limiter — the functional guard.

    Mirrors :func:`~office365.runtime.retry.retry`: it waits for the group gate,
    then feeds the outcome (returned response or ``exception.response``) back to
    the limiter. No call-site side effects; composable and thread-safe.

    Args:
        func: Callable performing one request/operation.
        gate: The shared :class:`RateLimiter` to pace against.
        scope: Optional throttling scope for per-scope pacing (see
            :meth:`RateLimiter.acquire`).
    """
    gate.acquire(scope)
    try:
        result = func()
    except Exception as ex:
        gate.observe(getattr(ex, "response", None))
        raise
    gate.observe(result)
    return result


async def paced_async(
    func: Callable[[], Awaitable[Response]],
    gate: "RateLimiter",
    scope: Optional[str] = None,
) -> Response:
    """Async twin of :func:`paced`: await the gate, then observe the outcome.

    Lets the async path reuse the exact pacing policy as the sync path — only
    the wait is a coroutine, so the event loop keeps running while the group
    gate is closed. The outcome (returned response or ``exception.response``)
    is fed back to the limiter, including on failure.

    Args:
        func: Coroutine performing one request/operation.
        gate: The shared :class:`RateLimiter` to pace against.
        scope: Optional throttling scope for per-scope pacing.
    """
    await gate.acquire_async(scope)
    try:
        result = await func()
    except Exception as ex:
        gate.observe(getattr(ex, "response", None))
        raise
    gate.observe(result)
    return result


class RateLimiter:
    """Thread-safe gate shared across workers so parallel requests pace as a group.

    Unlike :func:`throttle_guard` (reactive, per-context) and the per-request
    backoff in ``retry.py``, this limiter coordinates a *fleet* of clones/workers:
    before any request is sent it blocks until the group gate is open, and when
    any worker observes throttling it pauses the whole group.

    The pacing policy lives in the pure :func:`pace` / :func:`wait_delay`; this
    class is only the thread-safe state holder with injectable ``clock`` and
    ``sleep`` (so tests can run without real time). Opt-in — wrap a transport
    with :class:`~office365.runtime.transport.throttled_transport.ThrottledTransport`
    or attach it to a context with :meth:`bind`; the existing per-request retry
    remains as the safety net.
    """

    _SLEEP_GRANULARITY = 0.05

    def __init__(
        self,
        health_threshold: int = 80,
        min_interval: float = 0.0,
        percentage_threshold: float = 0.8,
        percentage_interval: float = 1.0,
        weight_by_resource_unit: bool = True,
        per_scope: bool = False,
        clock: Callable[[], float] = time.monotonic,
        sleep: Callable[[float], None] = time.sleep,
        async_sleep: Callable[[float], Awaitable[None]] = asyncio.sleep,
    ) -> None:
        self._lock = threading.Lock()
        self._state = PaceState()
        self._scope_states: dict[str, PaceState] = {}
        self._health_threshold = health_threshold
        self._min_interval = min_interval
        self._percentage_threshold = percentage_threshold
        self._percentage_interval = percentage_interval
        self._weight_by_resource_unit = weight_by_resource_unit
        self._per_scope = per_scope
        self._clock = clock
        self._sleep = sleep
        self._async_sleep = async_sleep
        self._last_reason: Optional[str] = None
        self._last_scope: Optional[str] = None

    @property
    def last_reason(self) -> Optional[str]:
        """The most recent Graph ``x-ms-throttle-information`` value, if any."""
        return self._last_reason

    @property
    def last_scope(self) -> Optional[str]:
        """The most recent Graph ``x-ms-throttle-scope`` value, if any."""
        return self._last_scope

    def snapshot(self, scope: Optional[str] = None) -> PaceState:
        """Return the current gate state (a pure value).

        With ``scope`` and ``per_scope=True`` this returns that scope's bucket,
        falling back to the global gate when the scope was never throttled.
        """
        with self._lock:
            if scope is not None:
                return self._scope_states.get(scope, self._state)
            return self._state

    def _wait(self, scope: Optional[str]) -> float:
        """Seconds until both the global and (optional) scope gate open."""
        wait = wait_delay(self._state, now=self._clock())
        if scope is not None:
            state = self._scope_states.get(scope)
            if state is not None:
                wait = max(wait, wait_delay(state, now=self._clock()))
        return wait

    def acquire(self, scope: Optional[str] = None) -> None:
        """Block the calling thread until the group gate opens.

        Called before a request is sent; safe to invoke from many threads. Pass
        ``scope`` (with ``per_scope=True``) to also honor that scope's bucket,
        so a throttle confined to one Graph scope doesn't stall unrelated work.

        Args:
            scope: Optional ``x-ms-throttle-scope`` the request belongs to.
        """
        while True:
            with self._lock:
                wait = self._wait(scope)
            if wait <= 0:
                return
            self._sleep(min(wait, self._SLEEP_GRANULARITY))

    async def acquire_async(self, scope: Optional[str] = None) -> None:
        """Await until the group gate opens without blocking the event loop.

        Async counterpart of :meth:`acquire`: the shared state is read under the
        same thread lock (a fast, non-blocking read) but the wait yields to the
        event loop, so concurrently-running tasks keep making progress. Only the
        wait step is async — the limiter never holds a loop-bound primitive, so
        a single limiter can pace both the synchronous and asynchronous paths.

        Args:
            scope: Optional ``x-ms-throttle-scope`` the request belongs to.
        """
        while True:
            with self._lock:
                wait = self._wait(scope)
            if wait <= 0:
                return
            await self._async_sleep(min(wait, self._SLEEP_GRANULARITY))

    def observe(self, response: Optional[Response]) -> None:
        """Record throttling signals and pause the group when the server asks.

        A response carrying ``x-ms-throttle-scope`` updates that scope's bucket;
        otherwise (or additionally, when not in ``per_scope`` mode) it updates
        the global gate. The last throttle reason/scope are remembered for
        logging.
        """
        if response is None:
            return
        limits = parse_throttling(response)
        if limits is None:
            return
        with self._lock:
            if limits.reason is not None:
                self._last_reason = limits.reason
            if limits.scope is not None:
                self._last_scope = limits.scope
            if self._per_scope and limits.scope is not None:
                self._scope_states[limits.scope] = pace(
                    self._scope_states.get(limits.scope, PaceState()),
                    limits,
                    now=self._clock(),
                    health_threshold=self._health_threshold,
                    min_interval=self._min_interval,
                    percentage_threshold=self._percentage_threshold,
                    percentage_interval=self._percentage_interval,
                    weight_by_resource_unit=self._weight_by_resource_unit,
                )
            else:
                self._state = pace(
                    self._state,
                    limits,
                    now=self._clock(),
                    health_threshold=self._health_threshold,
                    min_interval=self._min_interval,
                    percentage_threshold=self._percentage_threshold,
                    percentage_interval=self._percentage_interval,
                    weight_by_resource_unit=self._weight_by_resource_unit,
                )

    def bind(self, context: "ClientRuntimeContext") -> "RateLimiter":
        """Pace every request of a context (or ``clone``) by wrapping its transport.

        Delegates to :meth:`ClientRequest.with_rate_limiter` on the context's
        request, so the shared limiter gates each send and observes each response
        (and any error's ``response``).

        Args:
            context: The client context to gate.
        """
        context.pending_request().with_rate_limiter(self)
        return self

    def reset(self) -> None:
        """Clear the current gate (used by tests / recovery)."""
        with self._lock:
            self._state = PaceState()
            self._scope_states.clear()
            self._last_reason = None
            self._last_scope = None
