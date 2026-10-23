"""Async runtime tests (offline).

Covers the transport foundation and the async query terminals: the default
:meth:`BaseTransport.execute_async` offloads the blocking transport to a worker
thread, and ``execute_query_async`` mirrors the synchronous request lifecycle
(hooks, response processing, error dispatch) without blocking the event loop.
"""

from __future__ import annotations

import asyncio
import threading

import pytest
from office365.graph_client import GraphClient
from office365.runtime.client_request_exception import ClientRequestException
from office365.runtime.queries.client_query import ClientQuery
from office365.runtime.queries.deferred import DeferredOperationQuery
from office365.runtime.transport.base import BaseTransport
from office365.sharepoint.client_context import ClientContext
from tests._scripted_transport import AsyncScriptedTransport, ScriptedTransport, build_response

_URL = "https://contoso.sharepoint.com/_api/web"
_SITE_URL = "https://contoso.sharepoint.com"


def _context(payloads: list) -> tuple[ClientContext, ScriptedTransport]:
    ctx = ClientContext(_SITE_URL)
    ctx.pending_request().beforeExecute.clear()
    transport = ScriptedTransport(payloads)
    ctx.pending_request().transport = transport
    return ctx, transport


def test_deferred_query_resolves_without_request() -> None:
    ctx, transport = _context([])
    ctx.add_query(DeferredOperationQuery(ctx))

    asyncio.run(ctx.execute_query_async())

    assert transport.calls == 0


def test_execute_query_async_dispatches_to_on_error() -> None:
    ctx, _ = _context([{"status": 404, "body": {"error": {"message": "missing"}}}])
    handled: list[ClientRequestException] = []
    ctx.load(ctx.web)
    ctx.on_error(handled.append)

    asyncio.run(ctx.execute_query_async())

    assert len(handled) == 1


def test_execute_query_async_retry_exhausts() -> None:
    ctx, transport = _context([{"status": 500, "body": {}} for _ in range(3)])
    ctx.load(ctx.web)

    with pytest.raises(ClientRequestException):
        asyncio.run(ctx.execute_query_async_retry(max_retry=3, timeout_secs=0))

    assert transport.calls == 3  # noqa: PLR2004


def test_execute_query_async_retry_retries_connection_error() -> None:
    class _FlakyAsyncTransport(BaseTransport):
        def __init__(self, outcomes: list) -> None:
            self._outcomes = outcomes
            self.calls = 0

        def execute(self, request):
            raise AssertionError("async path must use execute_async")

        async def execute_async(self, request):
            outcome = self._outcomes[self.calls]
            self.calls += 1
            if isinstance(outcome, Exception):
                raise outcome
            return build_response(request, outcome)

    import requests

    ctx = ClientContext(_SITE_URL)
    ctx.pending_request().beforeExecute.clear()
    transport = _FlakyAsyncTransport([requests.ConnectionError("boom"), {"d": {"Title": "Contoso"}}])
    ctx.pending_request().with_async_transport(transport)
    ctx.load(ctx.web)

    asyncio.run(ctx.execute_query_async_retry(max_retry=3, timeout_secs=0))

    assert ctx.web.properties.get("Title") == "Contoso"
    assert transport.calls == 2  # noqa: PLR2004


def test_async_context_manager_closes_transport() -> None:
    closed: list[bool] = []

    class _ClosableTransport(ScriptedTransport):
        def close(self) -> None:
            closed.append(True)

    ctx = ClientContext(_SITE_URL)
    ctx.pending_request().transport = _ClosableTransport([])

    async def _run() -> None:
        async with ctx:
            pass

    asyncio.run(_run())

    assert closed == [True]


def test_clone_reuses_async_transport() -> None:
    """A clone keeps the explicitly configured async transport of its parent."""
    ctx = ClientContext(_SITE_URL)
    ctx.pending_request().beforeExecute.clear()
    async_transport = ScriptedTransport([{"d": {"Title": "Contoso"}}])
    ctx.pending_request().with_async_transport(async_transport)

    clone = ctx.clone(_SITE_URL)
    clone.pending_request().beforeExecute.clear()
    clone.load(clone.web)

    asyncio.run(clone.execute_query_async())

    assert clone.web.properties.get("Title") == "Contoso"
    assert async_transport.calls == 1


class _AsyncGraphBatchHarness(GraphClient):
    """GraphClient whose batch units are recorded instead of sent over HTTP."""

    def __init__(self) -> None:
        super().__init__()
        self.executed: list[object] = []
        self.thread_ids: list[int] = []
        self.max_active = 0
        self._active = 0
        self._lock = threading.Lock()

    async def _execute_batch_async(self, batch_qry):
        with self._lock:
            self._active += 1
            self.max_active = max(self.max_active, self._active)
        try:
            await asyncio.sleep(0.02)
            self.executed.append(batch_qry)
            self.thread_ids.append(threading.get_ident())
            return [batch_qry]
        finally:
            with self._lock:
                self._active -= 1


class _ThreadRecordingTransport(ScriptedTransport):
    """Transport that records the thread its (blocking) send runs on."""

    def __init__(self, payloads: list) -> None:
        super().__init__(payloads)
        self.threads: list[int] = []

    def execute(self, request):
        self.threads.append(threading.get_ident())
        return super().execute(request)


def _enqueue(ctx: GraphClient, count: int) -> None:
    ctx.pending_request().beforeExecute.clear()
    ctx.pending_request().authenticate_request = lambda request: None  # type: ignore[method-assign]
    for _ in range(count):
        ctx.add_query(ClientQuery(ctx))


def test_execute_batch_async_runs_batches_concurrently() -> None:
    ctx = _AsyncGraphBatchHarness()
    _enqueue(ctx, 4)
    results: list[list] = []

    asyncio.run(ctx.execute_batch_async(items_per_batch=1, concurrency=4, success_callback=results.append))

    assert len(results) == 4  # noqa: PLR2004
    assert len(ctx.executed) == 4  # noqa: PLR2004
    assert ctx.max_active > 1


def test_execute_batch_async_offloads_off_loop_thread() -> None:
    """The real Graph async batch sends through the configured async transport."""
    loop_thread = threading.get_ident()
    ctx = GraphClient()
    _enqueue(ctx, 1)
    transport = _ThreadRecordingTransport([{"responses": [{"id": "0", "status": 200, "headers": {}, "body": {}}]}])
    ctx.pending_request().with_async_transport(transport)

    asyncio.run(ctx.execute_batch_async(items_per_batch=1))

    assert transport.threads and transport.threads[0] != loop_thread


def test_execute_batch_async_raises_first_error() -> None:
    ctx = _AsyncGraphBatchHarness()

    async def _boom(batch_qry):
        raise RuntimeError("boom")

    ctx._execute_batch_async = _boom  # type: ignore[method-assign]
    _enqueue(ctx, 2)
    results: list[list] = []

    with pytest.raises(RuntimeError):
        asyncio.run(ctx.execute_batch_async(items_per_batch=1, concurrency=2, success_callback=results.append))

    assert results == []


def test_sharepoint_execute_batch_async_warms_up_and_splits() -> None:
    ctx = ClientContext(_SITE_URL)
    warmed: list[bool] = []
    ctx.pending_request().warm_up = lambda: warmed.append(True)  # type: ignore[method-assign]
    seen: list[object] = []

    async def _record(batch_qry):
        seen.append(batch_qry)
        return [batch_qry]

    ctx._execute_batch_async = _record  # type: ignore[method-assign]
    _enqueue(ctx, 2)

    asyncio.run(ctx.execute_batch_async(items_per_batch=1, concurrency=2))

    assert warmed == [True]
    assert len(seen) == 2  # noqa: PLR2004


def _queue_loads(ctx: ClientContext, count: int) -> None:
    for _ in range(count):
        ctx.load(ctx.web)


def _sp_page(items: list) -> dict:
    return {"d": {"results": [{"Id": i, "Title": f"Item {i}"} for i in items]}}


def test_get_all_async_follows_next_link() -> None:
    next_url = "https://graph.microsoft.com/v1.0/users?$skiptoken=abc"
    ctx = GraphClient()
    ctx.pending_request().beforeExecute.clear()
    transport = ScriptedTransport(
        [
            {"@odata.nextLink": next_url, "value": [{"id": "1"}, {"id": "2"}]},
            {"value": [{"id": "3"}]},
        ]
    )
    ctx.pending_request().transport = transport
    loaded: list[int] = []
    col = ctx.users

    asyncio.run(col.get_all_async(page_size=2, page_loaded=lambda _col: loaded.append(1)))

    assert [u.properties.get("id") for u in col] == ["1", "2", "3"]
    assert transport.calls == 2  # noqa: PLR2004
    assert loaded == [1, 1]


def test_get_all_async_dedupes_by_id() -> None:
    """Rows repeated across pages can be dropped with ``dedupe_by="id"``."""
    next_1 = "https://graph.microsoft.com/v1.0/users?$skiptoken=a"
    next_2 = "https://graph.microsoft.com/v1.0/users?$skiptoken=b"
    ctx = GraphClient()
    ctx.pending_request().beforeExecute.clear()
    transport = ScriptedTransport(
        [
            {"@odata.nextLink": next_1, "value": [{"id": "1"}, {"id": "2"}]},
            {"@odata.nextLink": next_2, "value": [{"id": "2"}, {"id": "3"}]},
            {"value": [{"id": "3"}, {"id": "4"}]},
        ]
    )
    ctx.pending_request().transport = transport
    col = ctx.users

    asyncio.run(col.get_all_async(page_size=2, dedupe_by="id"))

    assert [u.properties.get("id") for u in col] == ["1", "2", "3", "4"]
    assert transport.calls == 3  # noqa: PLR2004


def test_aiter_fetches_pages_lazily() -> None:
    """``async for`` pulls pages on demand, without a prior ``get_all_async``."""
    ctx = ClientContext(_SITE_URL)
    transport = ScriptedTransport([_sp_page([1, 2]), _sp_page([3, 4]), _sp_page([])])
    ctx.pending_request().beforeExecute.clear()
    ctx.pending_request().transport = transport
    col = ctx.web.lists

    async def _collect() -> list:
        return [lst.properties.get("Id") async for lst in col.paged(page_size=2)]

    assert asyncio.run(_collect()) == [1, 2, 3, 4]  # noqa: PLR2004
    assert transport.calls == 3  # noqa: PLR2004


def test_execute_query_parallel_async_processes_in_order_and_reports_progress() -> None:
    ctx, transport = _context([{"d": {"Title": f"T{i}"}} for i in range(3)])
    _queue_loads(ctx, 3)
    seen: list = []

    asyncio.run(ctx.execute_query_parallel_async(concurrency=3, progress=seen.append))

    assert [p.done for p in seen] == [1, 2, 3]
    assert seen[-1].total == 3  # noqa: PLR2004
    assert seen[-1].stage == "parallel"
    assert transport.calls == 3  # noqa: PLR2004


def test_execute_query_parallel_async_retries_transient() -> None:
    ctx, transport = _context(
        [
            {"status": 429, "retry_after": 0, "body": {}},
            {"d": {"Title": "Contoso"}},
        ]
    )
    ctx.load(ctx.web)

    asyncio.run(ctx.execute_query_parallel_async(concurrency=2, max_retry=3, timeout_secs=0))

    assert ctx.web.properties.get("Title") == "Contoso"
    assert transport.calls == 2  # noqa: PLR2004


def test_execute_query_parallel_async_requeues_exhausted_transient() -> None:
    ctx, transport = _context([{"status": 500, "body": {}}])
    ctx.load(ctx.web)

    with pytest.raises(ClientRequestException):
        asyncio.run(ctx.execute_query_parallel_async(concurrency=2, max_retry=1, timeout_secs=0))

    assert transport.calls == 1
    assert ctx.has_pending_request  # failed query kept for a retry


def test_execute_query_parallel_on_error_collects_and_continues() -> None:
    """A permanent failure is reported and skipped instead of aborting the batch."""
    ctx, transport = _context(
        [
            {"status": 404, "body": {"error": {"message": "missing"}}},
            {"d": {"Title": "Contoso"}},
        ]
    )
    _queue_loads(ctx, 2)
    errors: list[BaseException] = []

    ctx.execute_query_parallel(concurrency=2, on_error=lambda _qry, error: errors.append(error))

    assert len(errors) == 1
    assert isinstance(errors[0], ClientRequestException)
    assert ctx.web.properties.get("Title") == "Contoso"
    assert transport.calls == 2  # noqa: PLR2004
    assert not ctx.has_pending_request  # failed query is not re-queued


def test_execute_query_parallel_async_on_error_collects_and_continues() -> None:
    ctx, transport = _context(
        [
            {"status": 404, "body": {"error": {"message": "missing"}}},
            {"d": {"Title": "Contoso"}},
        ]
    )
    _queue_loads(ctx, 2)
    errors: list[BaseException] = []

    asyncio.run(ctx.execute_query_parallel_async(concurrency=2, on_error=lambda _qry, error: errors.append(error)))

    assert len(errors) == 1
    assert isinstance(errors[0], ClientRequestException)
    assert ctx.web.properties.get("Title") == "Contoso"
    assert transport.calls == 2  # noqa: PLR2004
    assert not ctx.has_pending_request


class _BlockingTransport(AsyncScriptedTransport):
    """Native-async transport whose requests never settle until cancelled."""

    def __init__(self) -> None:
        super().__init__([])
        self.started = 0
        self.finished = 0
        self.cancelled = 0
        self.all_started: asyncio.Event | None = None

    async def execute_async(self, request):
        self.started += 1
        if self.started >= 4 and self.all_started is not None:  # noqa: PLR2004
            self.all_started.set()
        try:
            await asyncio.sleep(3600)
        except asyncio.CancelledError:
            self.cancelled += 1
            raise
        self.finished += 1
        return build_response(request, {"d": {}})


def test_execute_query_parallel_async_cancels_in_flight_siblings() -> None:
    """Cancelling a parallel run must not leave sibling requests running."""
    transport = _BlockingTransport()
    ctx = ClientContext(_SITE_URL)
    ctx.pending_request().beforeExecute.clear()
    ctx.pending_request().transport = transport
    _queue_loads(ctx, 4)

    async def _scenario() -> None:
        # ``before_execute_async`` offloads hooks to a worker thread, so the
        # requests only start once the pool schedules them: wait on an event the
        # transport sets, not a fixed number of event-loop turns.
        transport.all_started = asyncio.Event()
        task = asyncio.ensure_future(ctx.execute_query_parallel_async(concurrency=4))
        await asyncio.wait_for(transport.all_started.wait(), timeout=5)
        task.cancel()
        with pytest.raises(asyncio.CancelledError):
            await task

    asyncio.run(_scenario())

    assert transport.finished == 0
    assert transport.cancelled == 4  # noqa: PLR2004


def test_execute_request_direct_async_returns_response() -> None:
    ctx, transport = _context([{"d": {"Title": "Contoso"}}])

    response = asyncio.run(ctx.execute_request_direct_async("web"))

    assert response.status_code == 200  # noqa: PLR2004
    assert response.json() == {"d": {"Title": "Contoso"}}
    assert transport.calls == 1


def test_incremental_retry_async_recovers() -> None:
    ctx, transport = _context(
        [
            {"status": 429, "retry_after": 0, "body": {}},
            {"d": {"Title": "Contoso"}},
        ]
    )
    ctx.load(ctx.web)

    asyncio.run(ctx.execute_query_with_incremental_retry_async(max_retry=3))

    assert ctx.web.properties.get("Title") == "Contoso"
    assert transport.calls == 2  # noqa: PLR2004


def test_client_result_async_retry_forwards_is_retriable() -> None:
    from office365.runtime.client_result import ClientResult

    ctx, transport = _context([{"status": 404, "body": {}}, {"d": {"Title": "Contoso"}}])
    result = ClientResult(ctx, {})
    ctx.load(ctx.web)

    asyncio.run(result.execute_query_async_retry(max_retry=3, timeout_secs=0, is_retriable=lambda _ex: True))

    assert transport.calls == 2  # noqa: PLR2004


def test_entity_async_wrappers_delegate_to_context() -> None:
    ctx = ClientContext(_SITE_URL)
    web = ctx.web
    seen: dict[str, object] = {}

    async def _fake_incremental(max_retry=5, max_delay=None, jitter=True):
        seen["incremental"] = (max_retry, max_delay, jitter)
        return ctx

    async def _fake_batch(items_per_batch=100, success_callback=None, concurrency=1, max_batch_bytes=None):
        seen["batch"] = (items_per_batch, concurrency, max_batch_bytes)
        return ctx

    ctx.execute_query_with_incremental_retry_async = _fake_incremental  # type: ignore[method-assign]
    ctx.execute_batch_async = _fake_batch  # type: ignore[method-assign]

    async def _run() -> None:
        assert await web.execute_query_with_incremental_retry_async(max_retry=2, jitter=False) is web
        assert await web.execute_batch_async(items_per_batch=7, concurrency=3) is web

    asyncio.run(_run())

    assert seen["incremental"] == (2, None, False)
    assert seen["batch"] == (7, 3, None)
