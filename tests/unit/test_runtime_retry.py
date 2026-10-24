"""Merged unit tests (consolidated; see git history for originals)."""

from __future__ import annotations

import asyncio
import threading
import time
import unittest
from datetime import datetime, timedelta, timezone
from email.utils import format_datetime
from unittest import mock

import pytest
import requests
from office365.graph_client import GraphClient
from office365.runtime.client_request_exception import ClientRequestException
from office365.runtime.http.request_options import RequestOptions
from office365.runtime.http.throttling import (
    PaceState,
    RateLimiter,
    ThrottleLimits,
    pace,
    paced_async,
    parse_throttling,
    throttle_guard,
)
from office365.runtime.operations import ProgressTracker
from office365.runtime.parallel import run_parallel
from office365.runtime.queries.client_query import ClientQuery
from office365.runtime.retry import (
    backoff_delay,
    is_transient_error,
    response_retry_after,
    retry,
    should_reset_connections,
)
from office365.runtime.transport.base import BaseTransport
from office365.runtime.transport.throttled_transport import ThrottledTransport
from office365.runtime.types.event_handler import EventHandler
from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.request import SharePointRequest
from office365.sharepoint.webs.context_web_information import ContextWebInformation
from requests import Response
from tests._scripted_transport import ScriptedTransport as _ScriptedTransport


def _make_error_response(status_code: int, headers: dict | None = None) -> Response:
    resp = Response()
    resp.status_code = status_code
    resp.url = "https://contoso.sharepoint.com/_api/web"
    resp.headers.update(headers or {})
    resp._content = b'{"error":{"code":"-1, System.Exception","message":"boom"}}'
    return resp


def _response_with_retry_after(value: str) -> Response:
    resp = Response()
    resp.status_code = 503
    resp.headers["Retry-After"] = value
    return resp


def _make_exception(status_code: int, headers: dict | None = None) -> ClientRequestException:
    return ClientRequestException.from_response(_make_error_response(status_code, headers))


def _make_context(outcomes: list[Exception | None]) -> tuple[ClientContext, mock.Mock]:
    """ClientContext whose execute_query replays the scripted outcomes.

    ``None`` signals a successful execution; an exception is raised as-is.
    Attempts are read from ``execute_query.call_count``.
    """
    ctx = ClientContext("https://contoso.sharepoint.com")
    execute_query = mock.Mock(side_effect=outcomes)
    ctx.execute_query = execute_query  # type: ignore[method-assign]
    return ctx, execute_query


class TestExecuteQueryRetry(unittest.TestCase):
    def test_retries_exhausted_raises_last_error(self):
        ctx, execute_query = _make_context([_make_exception(503), _make_exception(503), _make_exception(503)])

        with self.assertRaises(ClientRequestException) as cm:
            ctx.execute_query_retry(max_retry=2, timeout_secs=1)

        self.assertEqual(execute_query.call_count, 2)
        assert cm.exception.response is not None
        self.assertEqual(cm.exception.response.status_code, 503)

    def test_ssl_error_is_not_retried(self):
        ctx, execute_query = _make_context([requests.exceptions.SSLError("bad cert"), None])

        with mock.patch("office365.runtime.retry.sleep") as sleep_mock:
            with self.assertRaises(requests.exceptions.SSLError):
                ctx.execute_query_retry(max_retry=5, timeout_secs=1)

        self.assertEqual(execute_query.call_count, 1)
        sleep_mock.assert_not_called()

    def test_incremental_retry_falls_back_to_exponential_backoff(self):
        ctx, execute_query = _make_context([_make_exception(503), None])

        with mock.patch("office365.runtime.retry.sleep") as sleep_mock:
            ctx.execute_query_with_incremental_retry(max_retry=5, jitter=False)

        self.assertEqual(execute_query.call_count, 2)
        sleep_mock.assert_called_once_with(5)

    def test_retry_after_is_waited_by_default(self):
        """Microsoft's first instruction for a throttled request: wait what it asked for."""
        ctx, execute_query = _make_context([_make_exception(429, {"Retry-After": "7"}), None])

        with mock.patch("office365.runtime.retry.sleep") as sleep_mock:
            ctx.execute_query_retry(max_retry=5, timeout_secs=1, jitter=False)

        self.assertEqual(execute_query.call_count, 2)
        sleep_mock.assert_called_once_with(7)


class TestRetryFunction(unittest.TestCase):
    def test_retries_exhausted_raises_last_error(self):
        func = mock.Mock(side_effect=_make_exception(503))

        with self.assertRaises(ClientRequestException) as cm:
            retry(func, max_retry=2, timeout_secs=1)

        self.assertEqual(func.call_count, 2)
        assert cm.exception.response is not None
        self.assertEqual(cm.exception.response.status_code, 503)

    def test_invalid_url_is_not_retried(self):
        func = mock.Mock(side_effect=requests.exceptions.InvalidURL("nope"))

        with mock.patch("office365.runtime.retry.sleep") as sleep_mock:
            with self.assertRaises(requests.exceptions.InvalidURL):
                retry(func, max_retry=5, timeout_secs=1)

        self.assertEqual(func.call_count, 1)
        sleep_mock.assert_not_called()

    def test_max_delay_bounds_the_wait_the_server_asks_for(self):
        """A caller who names a ceiling keeps it, whatever ``Retry-After`` says."""
        func = mock.Mock(side_effect=[_make_exception(429, {"Retry-After": "600"}), None])

        with mock.patch("office365.runtime.retry.sleep") as sleep_mock:
            retry(func, max_retry=5, max_delay=30)

        sleep_mock.assert_called_once_with(30)


class TestTransportErrorClassification(unittest.TestCase):
    def test_connection_and_timeout_are_transient(self):
        self.assertTrue(is_transient_error(requests.ConnectionError("boom")))
        self.assertTrue(is_transient_error(requests.Timeout("slow")))
        self.assertTrue(is_transient_error(requests.exceptions.ChunkedEncodingError("cut")))

    def test_ssl_and_malformed_url_are_permanent(self):
        self.assertFalse(is_transient_error(requests.exceptions.SSLError("bad cert")))
        self.assertFalse(is_transient_error(requests.exceptions.InvalidURL("nope")))

    def test_reset_connections_predicate(self):
        self.assertTrue(should_reset_connections(_make_exception(503)))
        self.assertTrue(should_reset_connections(requests.ConnectionError("boom")))
        self.assertFalse(should_reset_connections(_make_exception(429)))
        self.assertFalse(should_reset_connections(_make_exception(400)))
        self.assertFalse(should_reset_connections(requests.exceptions.SSLError("bad cert")))


class TestRetryAfterDelay(unittest.TestCase):
    def test_parses_http_date(self):
        future = datetime.now(timezone.utc) + timedelta(seconds=30)
        value = format_datetime(future, usegmt=True)
        self.assertGreaterEqual(response_retry_after(_response_with_retry_after(value)), 28)
        self.assertLessEqual(response_retry_after(_response_with_retry_after(value)), 30)


class TestBackoffDelay(unittest.TestCase):
    def test_exponential_growth(self):
        self.assertEqual(backoff_delay(1, base=5, jitter=False), 5)
        self.assertEqual(backoff_delay(2, base=5, jitter=False), 10)  # noqa: PLR2004
        self.assertEqual(backoff_delay(3, base=5, jitter=False), 20)  # noqa: PLR2004

    def test_jitter_within_bounds(self):
        for attempt in (1, 2, 3):  # noqa: PLR2004
            nominal = backoff_delay(attempt, base=5, jitter=False)
            for _ in range(50):  # noqa: PLR2004
                delay = backoff_delay(attempt, base=5)
                self.assertGreaterEqual(delay, 0)
                self.assertLessEqual(delay, nominal)


class TestContextStateAfterRetryFailure(unittest.TestCase):
    """Issue #938 — execute_query_retry must not leave the context dirty."""

    def test_exhausted_retries_leave_queue_clean(self):
        from office365.runtime.queries.client_query import ClientQuery

        ctx = ClientContext("https://contoso.sharepoint.com")
        qry = ClientQuery(ctx)
        ctx.add_query(qry)
        attempts = {"n": 0}

        def _execute_query():
            attempts["n"] += 1
            if ctx._queries:
                ctx._current_query = ctx._queries.popleft()
            raise _make_exception(503)

        ctx.execute_query = _execute_query  # type: ignore[method-assign]

        with mock.patch("office365.runtime.retry.sleep"):
            with self.assertRaises(ClientRequestException):
                ctx.execute_query_retry(max_retry=3, timeout_secs=5, jitter=False)

        self.assertEqual(attempts["n"], 3)  # noqa: PLR2004
        # no stale query left queued and no cursor retained
        self.assertEqual(len(ctx._queries), 0)
        self.assertIsNone(ctx.current_query)


def throttling__response(headers: dict) -> Response:
    resp = Response()
    resp.status_code = 200
    resp.headers.update(headers)
    return resp


def test_parse_throttling_malformed_values():
    limits = parse_throttling(throttling__response({"RateLimit-Remaining": "abc", "RateLimit-Reset": "30"}))
    assert limits == ThrottleLimits(remaining=None, reset=30, status=200)
    assert limits is not None
    assert limits.remaining is None


def test_throttle_guard_attaches_and_detaches():
    client = GraphClient()
    seen = []

    with throttle_guard(client, on_limits=seen.append):
        client.pending_request().afterExecute(
            throttling__response({"RateLimit-Remaining": "7", "RateLimit-Reset": "10"})
        )
        assert len(seen) == 1
        assert seen[0].remaining == 7  # noqa: PLR2004

    # the hook is detached on exit — firing again does nothing
    client.pending_request().afterExecute(throttling__response({"RateLimit-Remaining": "1"}))
    assert len(seen) == 1


def ratelimiter__response(
    retry_after: str | None = None,
    health_score: str | None = None,
    limit_percentage: str | None = None,
    resource_unit: str | None = None,
    scope: str | None = None,
    reason: str | None = None,
) -> Response:
    resp = Response()
    resp.status_code = 429 if retry_after else 200
    resp.headers["Content-Type"] = "application/json"
    if retry_after:
        resp.headers["Retry-After"] = retry_after
    if health_score:
        resp.headers["X-SharePointHealthScore"] = health_score
    if limit_percentage:
        resp.headers["x-ms-throttle-limit-percentage"] = limit_percentage
    if resource_unit:
        resp.headers["x-ms-resource-unit"] = resource_unit
    if scope:
        resp.headers["x-ms-throttle-scope"] = scope
    if reason:
        resp.headers["x-ms-throttle-information"] = reason
    resp._content = b"{}"
    return resp


def _elapsed(fn) -> float:
    start = time.monotonic()
    fn()
    return time.monotonic() - start


class _FakeClock:
    def __init__(self) -> None:
        self.t = 0.0

    def __call__(self) -> float:
        return self.t


class TestRateLimiter(unittest.TestCase):
    def test_retry_after_gates_the_group(self):
        limiter = RateLimiter()
        limiter.observe(ratelimiter__response(retry_after="1"))

        elapsed = _elapsed(limiter.acquire)
        self.assertGreaterEqual(elapsed, 0.9)
        self.assertLess(elapsed, 2.0)

    def test_bind_wraps_transport_and_reports_to_limiter(self):
        ctx = ClientContext("https://contoso.sharepoint.com/sites/x")
        ctx.pending_request().beforeExecute.clear()
        inner = _ScriptedTransport([{"status": 429, "retry_after": 2, "body": {}}])
        ctx.pending_request().transport = inner
        limiter = RateLimiter()
        limiter.bind(ctx)

        wrapped = ctx.pending_request().transport
        self.assertIsInstance(wrapped, ThrottledTransport)
        self.assertIs(wrapped.inner, inner)

        with self.assertRaises(ClientRequestException):
            ctx.load(ctx.web).execute_query()

        # the 429 response observed by the wrapped transport must gate the group
        self.assertGreaterEqual(_elapsed(limiter.acquire), 1.8)

    def test_scope_signal_gates_the_group_by_default(self):
        limiter = RateLimiter(clock=_FakeClock(), sleep=lambda _delay: None)

        limiter.observe(ratelimiter__response(retry_after="5", scope="Mail.ReadWrite", reason="CPULimitExceeded"))

        self.assertGreaterEqual(limiter.snapshot().next_available_at, 5.0)
        self.assertEqual(limiter.last_scope, "Mail.ReadWrite")
        self.assertEqual(limiter.last_reason, "CPULimitExceeded")

    def test_per_scope_isolates_the_throttled_scope(self):
        clock = _FakeClock()
        slept: list[float] = []

        def _sleep(delay: float) -> None:
            slept.append(delay)
            clock.t += delay

        limiter = RateLimiter(per_scope=True, clock=clock, sleep=_sleep)
        limiter.observe(ratelimiter__response(retry_after="5", scope="Mail.ReadWrite"))

        # global gate is untouched and an unrelated scope is not gated
        self.assertEqual(limiter.snapshot().next_available_at, 0.0)
        limiter.acquire("Files.Read")
        self.assertEqual(slept, [])

        self.assertEqual(limiter.snapshot("Mail.ReadWrite").next_available_at, 5.0)
        limiter.acquire("Mail.ReadWrite")
        self.assertGreaterEqual(sum(slept), 5.0)

        limiter.reset()
        self.assertEqual(limiter.snapshot("Mail.ReadWrite").next_available_at, 0.0)
        self.assertIsNone(limiter.last_scope)


class _StubTransport(BaseTransport):
    def __init__(self, response: Response | None = None, error: Exception | None = None) -> None:
        self._response = response
        self._error = error
        self.closed = False

    def execute(self, request) -> Response:
        if self._error is not None:
            raise self._error
        assert self._response is not None
        return self._response

    @property
    def proxies(self) -> dict[str, str] | None:
        return {"https": "http://proxy"}

    @property
    def verify(self) -> bool | str:
        return False

    @property
    def timeout(self) -> int | None:
        return 7

    def close(self) -> None:
        self.closed = True


class TestPacedGuard(unittest.TestCase):
    def test_throttled_transport_delegates_and_paces(self):
        gate = mock.Mock()
        response = ratelimiter__response()
        inner = _StubTransport(response=response)
        transport = ThrottledTransport(inner, gate)

        self.assertEqual(transport.proxies, {"https": "http://proxy"})
        self.assertIs(transport.verify, False)
        self.assertEqual(transport.timeout, 7)  # noqa: PLR2004
        self.assertIs(transport.execute(RequestOptions(url="https://contoso.sharepoint.com")), response)
        gate.acquire.assert_called_once_with(None)
        gate.observe.assert_called_once_with(response)

        transport.close()
        self.assertTrue(inner.closed)

    def test_throttled_transport_observes_error(self):
        gate = mock.Mock()
        inner = _StubTransport(error=RuntimeError("down"))
        transport = ThrottledTransport(inner, gate)

        with self.assertRaises(RuntimeError):
            transport.execute(object())
        gate.acquire.assert_called_once_with(None)
        gate.observe.assert_called_once_with(None)


class TestPacedAsync(unittest.TestCase):
    def test_paced_async_observes_error_response_and_reraises(self):
        gate = mock.Mock()
        gate.acquire_async = mock.AsyncMock()
        err = ClientRequestException("boom", response=ratelimiter__response(retry_after="3"))

        async def _boom():
            raise err

        with self.assertRaises(ClientRequestException):
            asyncio.run(paced_async(_boom, gate))
        gate.observe.assert_called_once_with(err.response)

    def test_throttled_transport_execute_async_paces(self):
        gate = mock.Mock()
        gate.acquire_async = mock.AsyncMock()
        response = ratelimiter__response()
        inner = _StubTransport(response=response)
        transport = ThrottledTransport(inner, gate)

        result = asyncio.run(transport.execute_async(RequestOptions(url="https://contoso.sharepoint.com")))

        self.assertIs(result, response)
        gate.acquire_async.assert_awaited_once_with(None)
        gate.observe.assert_called_once_with(response)


class _Pending:
    def __init__(self) -> None:
        self.beforeExecute = EventHandler()
        self.afterExecute = EventHandler()
        self.onError = EventHandler()
        self.transport = _StubTransport()

    def with_rate_limiter(self, limiter) -> "_Pending":
        self.transport = ThrottledTransport(self.transport, limiter)
        return self


class _FakeContext:
    def __init__(self) -> None:
        self.pending = _Pending()

    def pending_request(self):
        return self.pending


class TestRunParallel(unittest.TestCase):
    def test_context_factory_once_per_thread_and_limiter_bound(self):
        contexts = []
        lock = threading.Lock()

        def factory():
            ctx = _FakeContext()
            with lock:
                contexts.append(ctx)
            return ctx

        def _worker(ctx, task):
            time.sleep(0.02)  # keep both pool threads busy so both create a context
            return (id(ctx), task)

        results = run_parallel(
            _worker,
            [1, 2, 3, 4],  # noqa: PLR2004
            concurrency=2,  # noqa: PLR2004
            context_factory=factory,  # type: ignore[arg-type]
        )

        self.assertEqual(len(contexts), 2)  # noqa: PLR2004 — one context per worker thread
        self.assertEqual(len({r[0] for r in results}), 2)  # noqa: PLR2004
        for ctx in contexts:
            self.assertIsInstance(ctx.pending.transport, ThrottledTransport)


def test_report_emits_progress_with_total():
    seen = []
    tracker = ProgressTracker(seen.append, total=10, stage="uploading")

    tracker.report(3)
    tracker.report(5)

    assert [p.done for p in seen] == [3, 5]
    assert all(p.total == 10 for p in seen)  # noqa: PLR2004
    assert all(p.stage == "uploading" for p in seen)


def test_advance_and_late_total():
    seen = []
    tracker = ProgressTracker(seen.append, stage="migrating")

    tracker.advance()
    tracker.advance(2)
    tracker.set_total(10)
    tracker.report(5)

    assert [p.done for p in seen] == [1, 3, 5]
    assert seen[-1].total == 10  # noqa: PLR2004
    assert seen[-1].percent == 50.0  # noqa: PLR2004


def test_thread_safe_advances_sum_to_total():
    seen = []
    tracker = ProgressTracker(seen.append, total=1000, stage="parallel")
    threads = [threading.Thread(target=lambda: [tracker.advance() for _ in range(100)]) for _ in range(10)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    assert tracker.done == 1000  # noqa: PLR2004
    assert len(seen) == 1000  # noqa: PLR2004


def _run_concurrently(target, count: int = 2) -> None:
    barrier = threading.Barrier(count)

    def _wrapped():
        barrier.wait()
        target()

    threads = [threading.Thread(target=_wrapped) for _ in range(count)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()


class TestThreadSafety(unittest.TestCase):
    def test_ensure_form_digest_single_flight(self):
        request = SharePointRequest("https://contoso.sharepoint.com")
        context_info = ContextWebInformation(FormDigestValue="digest", FormDigestTimeoutSeconds=1800)
        fetch = mock.Mock(return_value=context_info)
        request._fetch_context_web_information = fetch  # type: ignore[method-assign]

        requests_with_header = []

        def _ensure():
            req = RequestOptions("https://contoso.sharepoint.com")
            request.ensure_form_digest(req)
            requests_with_header.append(req)

        _run_concurrently(_ensure)

        fetch.assert_called_once()
        self.assertTrue(all(req.headers.get("X-RequestDigest") == "digest" for req in requests_with_header))

    def test_split_batches_preserves_order_and_drains_queue(self):
        ctx = ClientContext("https://contoso.sharepoint.com")
        for _ in range(250):
            ctx.add_query(ClientQuery(ctx))

        batches = ctx._split_batches(100)

        self.assertEqual([len(batch.queries) for batch in batches], [100, 100, 50])
        self.assertFalse(ctx.has_pending_request)
        self.assertIsNone(ctx._current_query)

    def test_clone_shares_auth_and_transport(self):
        ctx = ClientContext("https://contoso.sharepoint.com")
        ctx.add_query(ClientQuery(ctx))
        source_request = ctx.pending_request()

        clone = ctx.clone("https://contoso-admin.sharepoint.com")

        clone_request = clone.pending_request()
        self.assertIs(clone_request.authentication_context, source_request.authentication_context)
        self.assertIs(clone_request.transport, source_request.transport)
        self.assertFalse(clone.has_pending_request)
        self.assertTrue(ctx.has_pending_request)
        # Routing follows the clone URL even though the auth context (whose
        # ``url`` is the source site) is shared by reference; deriving the
        # service root from the auth context silently sent clone requests to
        # the source site.
        self.assertEqual(clone_request.base_url, "https://contoso-admin.sharepoint.com")
        self.assertEqual(clone_request.service_root_url, "https://contoso-admin.sharepoint.com/_api")
        self.assertEqual(source_request.service_root_url, "https://contoso.sharepoint.com/_api")

    def test_clone_keeps_pending_queries(self):
        ctx = ClientContext("https://contoso.sharepoint.com")
        for _ in range(3):
            ctx.add_query(ClientQuery(ctx))

        clone = ctx.clone("https://contoso-admin.sharepoint.com", clear_queries=False)

        self.assertEqual(len(clone._queries), 3)
        self.assertTrue(clone.has_pending_request)


# ── Graph throttling signals + priority ──────────────────────────────────────


def test_parse_throttling_graph_headers():
    limits = parse_throttling(
        throttling__response(
            {
                "Retry-After": "10",
                "x-ms-throttle-limit-percentage": "1.2",
                "x-ms-resource-unit": "3",
                "x-ms-throttle-scope": "Tenant_Application/ReadWrite/app/tenant",
                "x-ms-throttle-information": "WriteLimitExceeded",
            }
        )
    )
    assert limits is not None
    assert limits.retry_after == 10  # noqa: PLR2004
    assert limits.limit_percentage == 1.2  # noqa: PLR2004
    assert limits.resource_unit == 3  # noqa: PLR2004
    assert limits.scope == "Tenant_Application/ReadWrite/app/tenant"
    assert limits.reason == "WriteLimitExceeded"


def test_pace_reacts_to_graph_limit_percentage():
    now = 1000.0
    assert pace(PaceState(), ThrottleLimits(limit_percentage=1.2), now=now).next_available_at > now
    # below the threshold -> no pacing
    assert pace(PaceState(), ThrottleLimits(limit_percentage=0.5), now=now) == PaceState()


def test_with_throttle_priority_sets_request_header():
    client = GraphClient()
    client.pending_request().beforeExecute.clear()
    client.with_throttle_priority("high")
    request = RequestOptions(url="https://graph.microsoft.com/v1.0/me")

    client.pending_request().beforeExecute(request)

    assert request.headers.get("x-ms-throttle-priority") == "high"


def test_with_throttle_priority_rejects_bad_value():
    with pytest.raises(ValueError, match="priority"):
        GraphClient().with_throttle_priority("urgent")


def test_retry_decorator_retries_and_forwards_args():
    calls = {"n": 0}

    @retry(max_retry=3, timeout_secs=0, jitter=False)
    def flaky(value):
        calls["n"] += 1
        if calls["n"] < 2:  # noqa: PLR2004
            raise ClientRequestException("429")
        return value

    with mock.patch("office365.runtime.retry.sleep"):
        assert flaky("ok") == "ok"
    assert calls["n"] == 2  # noqa: PLR2004
