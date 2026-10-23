"""Tests for parallel query execution (pipelined I/O) on the runtime context."""

from __future__ import annotations

import threading
import time
from unittest import mock

from office365.graph_client import GraphClient
from office365.runtime.client_result import ClientResult
from office365.runtime.queries.function import FunctionQuery
from office365.runtime.transport.base import BaseTransport
from requests import Response


class _ConcurrencyTransport(BaseTransport):
    """Records the peak number of in-flight requests."""

    def __init__(self, delay: float = 0.05) -> None:
        super().__init__()
        self._delay = delay
        self._lock = threading.Lock()
        self.active = 0
        self.max_active = 0

    def execute(self, request):
        with self._lock:
            self.active += 1
            self.max_active = max(self.max_active, self.active)
        time.sleep(self._delay)
        with self._lock:
            self.active -= 1
        return _json_response(request)


class _FlakyTransport(BaseTransport):
    """Fails the first request with 503, then succeeds."""

    def __init__(self) -> None:
        super().__init__()
        self.calls = 0

    def execute(self, request):
        self.calls += 1
        resp = _json_response(request)
        if self.calls == 1:
            resp.status_code = 503
            resp.headers["Retry-After"] = "0"
        return resp


def _json_response(request) -> Response:
    resp = Response()
    resp.status_code = 200
    resp.url = request.url
    resp.headers["Content-Type"] = "application/json"
    resp._content = b"{}"
    return resp


def _client(transport) -> GraphClient:
    client = GraphClient()
    client.pending_request().beforeExecute.clear()  # no auth handler during offline build
    client.pending_request().transport = transport
    return client


def _queue(client: GraphClient, sink: list, index: int) -> None:
    result = ClientResult(client)
    query = FunctionQuery(client.me, "someOperation", None, result)
    client.add_query(query)
    result.after_execute(lambda _r, i=index: sink.append(i))


def test_run_parallel_on_error_collects_and_keeps_going():
    from office365.runtime.parallel import run_parallel

    def _worker(_ctx, task):
        if task == 2:  # noqa: PLR2004
            raise RuntimeError("boom")
        return task

    seen = []
    results = run_parallel(_worker, [1, 2, 3], concurrency=3, progress=seen.append, on_error=lambda _t, _e: None)

    assert results == [1, None, 3]
    assert len(seen) == 3  # noqa: PLR2004


def test_execute_query_parallel_retries_transient_failure():
    transport = _FlakyTransport()
    client = _client(transport)
    sink: list = []
    _queue(client, sink, 0)

    with mock.patch("office365.runtime.retry.sleep"):
        client.execute_query_parallel(concurrency=2)

    assert transport.calls == 2  # noqa: PLR2004 — 503 then retried
    assert sink == [0]


def test_execute_query_parallel_falls_back_to_serial():
    transport = _ConcurrencyTransport(delay=0.01)
    client = _client(transport)
    sink: list = []
    for index in range(3):
        _queue(client, sink, index)

    client.execute_query_parallel(concurrency=1)

    assert transport.max_active == 1  # sequential
    assert sink == [0, 1, 2]
