"""Merged unit tests (consolidated; see git history for originals)."""

from __future__ import annotations

import asyncio
import json as jsonlib
import threading
import time
import unittest
from typing import cast
from unittest import mock

import pytest
from office365.graph_client import GraphClient
from office365.runtime.client_object import ClientObject
from office365.runtime.client_request_exception import ClientRequestException
from office365.runtime.odata.batch_util import (
    WHOLE_BATCH_REJECT_CODES,
    WholeBatchRejected,
    estimate_query_bytes,
    partition_by_limits,
)
from office365.runtime.odata.v3.batch_request import ODataBatchV3Request
from office365.runtime.odata.v3.json_light_format import JsonLightFormat
from office365.runtime.odata.v4.batch_request import ODataV4BatchRequest
from office365.runtime.odata.v4.json_format import V4JsonFormat
from office365.runtime.paths.resource_path import ResourcePath
from office365.runtime.queries.batch import BatchQuery
from office365.runtime.queries.client_query import ClientQuery
from office365.runtime.queries.read_entity import ReadEntityQuery
from office365.runtime.transport.base import BaseTransport
from office365.runtime.transport.requests_transport import RequestsTransport
from office365.runtime.transport.throttled_transport import ThrottledTransport
from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.documentmanagement.document_set import DocumentSet
from requests import Response


def _make_batches(ctx: ClientContext, count: int) -> list[BatchQuery]:
    return [BatchQuery(ctx) for _ in range(count)]


class _ParallelHarness(ClientContext):
    def __init__(self) -> None:
        super().__init__("https://contoso.sharepoint.com")
        self.executed: list[object] = []
        self.max_active = 0
        self._active = 0
        self._lock = threading.Lock()

    def _execute_batch(self, batch_qry):
        with self._lock:
            self._active += 1
            self.max_active = max(self.max_active, self._active)
        time.sleep(0.05)
        with self._lock:
            self._active -= 1
        self.executed.append(batch_qry)
        return [batch_qry]


class TestExecuteBatchesInParallel(unittest.TestCase):
    def test_batches_run_concurrently(self):
        ctx = _ParallelHarness()
        batches = _make_batches(ctx, 4)

        results = []
        ctx._execute_batches_in_parallel(batches, concurrency=4, success_callback=results.append)

        self.assertEqual(len(results), 4)
        self.assertEqual(len(ctx.executed), 4)
        self.assertGreater(ctx.max_active, 1)

    def test_failure_re_raised_without_success_callback(self):
        ctx = _ParallelHarness()

        def _boom(batch_qry):
            raise RuntimeError("boom")

        ctx._execute_batch = _boom  # type: ignore[method-assign]

        results = []
        batches = _make_batches(ctx, 2)
        with self.assertRaises(RuntimeError):
            ctx._execute_batches_in_parallel(batches, concurrency=2, success_callback=results.append)

        self.assertEqual(results, [])


def _envelope(sub_statuses: list[int], retry_after: int | None = None) -> dict:
    responses = []
    for index, status in enumerate(sub_statuses):
        sub = {"id": str(index), "status": status, "headers": {}, "body": {}}
        if status == 429:  # noqa: PLR2004
            sub["headers"]["Retry-After"] = str(retry_after or 1)
            sub["body"] = {"error": {"code": "TooManyRequests", "message": "slow down"}}
        responses.append(sub)
    return {"responses": responses}


class _FakeTransport(BaseTransport):
    def __init__(self, payloads: list[dict]) -> None:
        self._payloads = payloads
        self.calls = 0
        self.request_payloads: list[dict] = []

    def execute(self, request):
        payload = self._payloads[min(self.calls, len(self._payloads) - 1)]
        self.calls += 1
        self.request_payloads.append(cast(dict, request.data))
        resp = Response()
        resp.status_code = 200
        resp.url = request.url
        resp._content = jsonlib.dumps(payload).encode("utf-8")
        return resp


def _make_batch(client: GraphClient, count: int) -> BatchQuery:
    client.pending_request().beforeExecute.clear()  # no auth handler during offline payload build
    return BatchQuery(client, [ClientQuery(client) for _ in range(count)])


class TestBatchSubRequestRetry(unittest.TestCase):
    def test_retries_only_failed_subrequests(self):
        client = GraphClient()
        transport = _FakeTransport([_envelope([200, 429], retry_after=1), _envelope([200])])
        req = ODataV4BatchRequest("", V4JsonFormat())
        req.transport = transport

        with mock.patch("office365.runtime.retry.sleep"):
            req.execute_query_with_retry(_make_batch(client, 2), max_retry=3, base_delay=1, jitter=False)

        # two batch round-trips: the full batch, then only the failed sub-request
        self.assertEqual(transport.calls, 2)
        self.assertEqual(len(transport.request_payloads[0]["requests"]), 2)
        self.assertEqual(len(transport.request_payloads[1]["requests"]), 1)

    def test_succeeds_on_first_round_trip(self):
        client = GraphClient()
        transport = _FakeTransport([_envelope([200, 200])])
        req = ODataV4BatchRequest("", V4JsonFormat())
        req.transport = transport

        req.execute_query_with_retry(_make_batch(client, 2), max_retry=3)

        self.assertEqual(transport.calls, 1)

    def test_non_transient_sub_failure_raises_without_retry(self):
        client = GraphClient()
        transport = _FakeTransport([_envelope([200, 400])])
        req = ODataV4BatchRequest("", V4JsonFormat())
        req.transport = transport

        with self.assertRaises(ClientRequestException):
            req.execute_query_with_retry(_make_batch(client, 2), max_retry=3)

        self.assertEqual(transport.calls, 1)

    def test_retries_exhausted_raises(self):
        client = GraphClient()
        transport = _FakeTransport([_envelope([429]), _envelope([429]), _envelope([429])])
        req = ODataV4BatchRequest("", V4JsonFormat())
        req.transport = transport

        with mock.patch("office365.runtime.retry.sleep"):
            with self.assertRaises(ClientRequestException):
                req.execute_query_with_retry(_make_batch(client, 1), max_retry=2, base_delay=1, jitter=False)

        self.assertEqual(transport.calls, 2)

    def test_honors_longest_retry_after(self):
        client = GraphClient()
        transport = _FakeTransport([_envelope([429, 429], retry_after=7), _envelope([200, 200])])
        req = ODataV4BatchRequest("", V4JsonFormat())
        req.transport = transport

        with mock.patch("office365.runtime.retry.sleep") as sleep_mock:
            req.execute_query_with_retry(_make_batch(client, 2), max_retry=3, jitter=False)

        sleep_mock.assert_called_once_with(7)


class TestBatchTransportSharing(unittest.TestCase):
    def test_execute_batch_shares_context_transport_across_workers(self):
        ctx = ClientContext("https://contoso.sharepoint.com")
        ctx.pending_request().beforeExecute.clear()
        transport = _FakeTransport([])
        ctx.pending_request().transport = transport
        captured: list[object] = []
        real_cls = ODataBatchV3Request

        def _factory(base_url, json_format, transport=None):
            captured.append(transport)
            req = real_cls(base_url, json_format, transport=transport)
            req.execute_query_with_retry = mock.Mock()
            return req

        with mock.patch("office365.sharepoint.client_context.ODataBatchV3Request", side_effect=_factory):
            ctx._execute_batch(BatchQuery(ctx))
            ctx._execute_batch(BatchQuery(ctx))

        self.assertIs(captured[0], transport)
        self.assertIs(captured[0], captured[1])

    def test_with_rate_limit_wraps_the_context_transport(self):
        ctx = ClientContext("https://contoso.sharepoint.com")
        inner = _FakeTransport([])
        ctx.pending_request().transport = inner

        ctx.with_rate_limit(min_interval=0.0)

        wrapped = ctx.pending_request().transport
        self.assertIsInstance(wrapped, ThrottledTransport)
        self.assertIs(wrapped.inner, inner)

    def test_context_rate_limiter_accessor(self):
        ctx = ClientContext("https://contoso.sharepoint.com")
        self.assertIsNone(ctx.rate_limiter)

        ctx.with_rate_limit(min_interval=0.0)

        self.assertIsNotNone(ctx.rate_limiter)
        self.assertIs(ctx.rate_limiter, ctx.pending_request().rate_limiter)

    def test_request_with_rate_limit_wraps_and_is_preserved(self):
        req = ODataBatchV3Request("https://contoso.sharepoint.com", JsonLightFormat())

        req.with_rate_limit(min_interval=0.0)
        limiter = req.rate_limiter
        self.assertIsInstance(req.transport, ThrottledTransport)
        self.assertIs(req.transport.limiter, limiter)

        # re-configuring the transport keeps the limiter
        req.with_transport(verify=False)
        self.assertIsInstance(req.transport, ThrottledTransport)
        self.assertIs(req.transport.limiter, limiter)

        # re-applying with_rate_limit replaces the limiter without stacking
        req.with_rate_limit(min_interval=0.0)
        self.assertIsInstance(req.transport, ThrottledTransport)
        self.assertIsInstance(req.transport.inner, RequestsTransport)
        self.assertIsNot(req.transport.limiter, limiter)

    def test_async_transport_is_wrapped_when_limiter_configured(self):
        req = ODataBatchV3Request("https://contoso.sharepoint.com", JsonLightFormat())
        req.with_rate_limit(min_interval=0.0)
        inner = _FakeTransport([])

        req.with_async_transport(inner)

        wrapped = req.async_transport
        self.assertIsInstance(wrapped, ThrottledTransport)
        self.assertIs(wrapped.inner, inner)
        self.assertIs(wrapped.limiter, req.rate_limiter)

    def test_limiter_configured_after_async_transport_wraps_it(self):
        req = ODataBatchV3Request("https://contoso.sharepoint.com", JsonLightFormat())
        inner = _FakeTransport([])
        req.with_async_transport(inner)
        self.assertIs(req.async_transport, inner)

        req.with_rate_limit(min_interval=0.0)

        wrapped = req.async_transport
        self.assertIsInstance(wrapped, ThrottledTransport)
        self.assertIs(wrapped.inner, inner)

    def test_async_transport_is_untouched_without_limiter(self):
        req = ODataBatchV3Request("https://contoso.sharepoint.com", JsonLightFormat())
        inner = _FakeTransport([])

        req.with_async_transport(inner)

        self.assertIs(req.async_transport, inner)

    def test_reapplying_limiter_does_not_stack_async_wrapper(self):
        req = ODataBatchV3Request("https://contoso.sharepoint.com", JsonLightFormat())
        inner = _FakeTransport([])
        req.with_rate_limit(min_interval=0.0)
        req.with_async_transport(inner)
        first = req.async_transport

        req.with_rate_limit(min_interval=0.0)

        second = req.async_transport
        self.assertIsInstance(second, ThrottledTransport)
        self.assertIs(second.inner, inner)
        self.assertIsNot(second.limiter, first.limiter)


class _FakeQuery:
    def __init__(self, url: str, payload: dict | str | None = None, headers: dict | None = None):
        self.url = url
        self.parameters_type = payload
        self.custom_headers = headers or {}


def test_partition_respects_item_cap():
    queries = [_FakeQuery("u") for _ in range(7)]
    batches = partition_by_limits(queries, max_items=3, max_bytes=None)
    assert [len(b) for b in batches] == [3, 3, 1]
    assert [q.url for q in batches[0]] == ["u", "u", "u"]  # order preserved


def test_partition_respects_byte_cap():
    queries = [
        _FakeQuery("u", {"data": "a" * 100}),
        _FakeQuery("u", {"data": "b" * 100}),
        _FakeQuery("u", {"data": "c" * 100}),
    ]
    batches = partition_by_limits(queries, max_items=None, max_bytes=estimate_query_bytes(queries[0]) * 2 + 200)
    assert len(batches) >= 2  # noqa: PLR2004 — big payloads don't all land in one batch


def test_estimate_matches_the_body_the_profile_builds():
    """The estimate is of the body that will be sent: a value nested in the
    parameters is serialized with its type marker, not repr()'d."""

    class _Value:
        entity_type_name = "SP.Thing"

        def to_json(self, json_format=None):
            return {"x": 1} if json_format is None else {"x": 1, "__metadata": {"type": "SP.Thing"}}

    measured = _FakeQuery("u", {"thing": _Value()})
    as_sent = _FakeQuery("u", {"thing": {"x": 1, "__metadata": {"type": "SP.Thing"}}})

    assert estimate_query_bytes(measured, JsonLightFormat()) == estimate_query_bytes(as_sent)


def test_oversized_single_stays_alone():
    huge = _FakeQuery("u", {"data": "x" * 100000})
    queries = [huge, _FakeQuery("u", None)]
    batches = partition_by_limits(queries, max_items=None, max_bytes=1000)
    assert len(batches) == 2  # noqa: PLR2004
    assert len(batches[0]) == 1


def test_whole_batch_reject_marker_carries_queries_and_cause():
    cause = ClientRequestException("400 body too large")
    reject = WholeBatchRejected([_FakeQuery("u")], cause)
    assert len(reject.queries) == 1
    assert reject.__cause__ is cause
    assert 413 in WHOLE_BATCH_REJECT_CODES  # noqa: PLR2004


# ── v3: GETs stay outside change sets (#871) ─────────────────────────────────


def test_function_query_get_is_not_a_change_set():
    """#871: File.get_content() is a GET ($value) and must not be wrapped in a change set."""
    ctx = ClientContext("https://contoso.sharepoint.com")
    ctx.pending_request().beforeExecute.clear()  # offline: no auth handler

    file = ctx.web.get_file_by_server_relative_path("/sites/x/Shared Documents/a.txt")
    content = file.get_content()

    batch = BatchQuery(ctx, list(ctx._queries))
    assert [type(q).__name__ for q in batch.get_queries] == ["FunctionQuery"]
    assert batch.change_sets == []
    assert batch.has_change_sets is False
    assert content in [q.return_type for q in batch.get_queries]

    # A GET-only batch is a plain multipart/mixed request with no change set part.
    payload = ODataBatchV3Request("https://contoso.sharepoint.com", JsonLightFormat())._prepare_payload(batch)
    assert b"changeset" not in payload.lower()


def test_mixed_batch_separates_get_from_change_set():
    """A GET plus an action: only the action is a change set; the GET runs at top level."""
    ctx = ClientContext("https://contoso.sharepoint.com")
    ctx.pending_request().beforeExecute.clear()

    file = ctx.web.get_file_by_server_relative_path("/sites/x/Shared Documents/a.txt")
    file.get_content()  # FunctionQuery -> GET
    file.open_binary_stream()  # ServiceOperationQuery -> POST

    batch = BatchQuery(ctx, list(ctx._queries))
    assert [type(q).__name__ for q in batch.get_queries] == ["FunctionQuery"]
    assert [type(q).__name__ for q in batch.change_sets] == ["ServiceOperationQuery"]
    assert batch.ordered_queries == batch.change_sets + batch.get_queries

    payload = ODataBatchV3Request("https://contoso.sharepoint.com", JsonLightFormat())._prepare_payload(batch)
    assert b"changeset" in payload.lower()


def test_batch_function_query_returns_binary_content():
    """#871: a batched File.get_content() returns raw bytes, not a decoded text line."""
    ctx = ClientContext("https://contoso.sharepoint.com")
    ctx.pending_request().beforeExecute.clear()

    file = ctx.web.get_file_by_server_relative_path("/sites/x/Shared Documents/a.bin")
    content = file.get_content()
    batch = BatchQuery(ctx, list(ctx._queries))

    binary = b"\x00\x01\n\xff\xfe raw\r\nbytes"
    body = (
        b"--batch_response\r\n"
        b"Content-Type: application/http\r\n"
        b"Content-Transfer-Encoding: binary\r\n\r\n"
        b"HTTP/1.1 200 OK\r\n"
        b"Content-Type: application/octet-stream\r\n\r\n" + binary + b"\r\n--batch_response--\r\n"
    )
    response = Response()
    response.status_code = 200
    response.headers["Content-Type"] = "multipart/mixed; boundary=batch_response"
    response._content = body

    ODataBatchV3Request("https://contoso.sharepoint.com", JsonLightFormat()).handle_response(response, batch)

    assert content.value == binary


# ── Graph dependsOn sequencing (v4) ──────────────────────────────────────────


def _payload_requests(transport: _FakeTransport, call: int = 0) -> list[dict]:
    return cast(list, transport.request_payloads[call]["requests"])


def test_sequential_emits_depends_on_chain():
    client = GraphClient()
    transport = _FakeTransport([_envelope([200, 200, 200])])
    req = ODataV4BatchRequest("", V4JsonFormat())
    req.transport = transport
    batch = _make_batch(client, 3)
    batch.sequential = True

    req.execute_query_with_retry(batch, max_retry=1)

    requests = _payload_requests(transport)
    assert "dependsOn" not in requests[0]
    assert requests[1]["dependsOn"] == ["0"]
    assert requests[2]["dependsOn"] == ["1"]


def test_parallel_batch_has_no_depends_on():
    client = GraphClient()
    transport = _FakeTransport([_envelope([200, 200])])
    req = ODataV4BatchRequest("", V4JsonFormat())
    req.transport = transport

    req.execute_query_with_retry(_make_batch(client, 2), max_retry=1)

    assert all("dependsOn" not in item for item in _payload_requests(transport))


def test_response_id_maps_to_submission_order():
    client = GraphClient()
    client.pending_request().beforeExecute.clear()  # no auth handler during offline payload build
    obj = ClientObject(client, ResourcePath("me"))
    read = ReadEntityQuery(obj, ["displayName"])
    write = ClientQuery(client)
    batch = BatchQuery(client, [read, write])
    assert batch.ordered_queries == [write, read]  # re-groups (non-GET first)

    payload = ODataV4BatchRequest("", V4JsonFormat())._prepare_payload(batch)
    assert [item["id"] for item in payload["requests"]] == ["0", "1"]

    response = Response()
    response._content = jsonlib.dumps(_envelope([200, 200])).encode("utf-8")
    mapped = [qry for qry, _ in ODataV4BatchRequest._extract_response(response, batch)]
    assert mapped == [read, write]


def test_sequential_survives_retry():
    client = GraphClient()
    transport = _FakeTransport([_envelope([200, 429], retry_after=1), _envelope([200])])
    req = ODataV4BatchRequest("", V4JsonFormat())
    req.transport = transport
    batch = _make_batch(client, 2)
    batch.sequential = True

    with mock.patch("office365.runtime.retry.sleep"):
        req.execute_query_with_retry(batch, max_retry=3, base_delay=1, jitter=False)

    assert _payload_requests(transport, 0)[1]["dependsOn"] == ["0"]
    retry_requests = _payload_requests(transport, 1)
    assert len(retry_requests) == 1
    assert "dependsOn" not in retry_requests[0]  # subset of one -> no dependency


def test_execute_batch_rejects_sequential_with_concurrency():
    with pytest.raises(ValueError, match="concurrency=1"):
        GraphClient().execute_batch(sequential=True, concurrency=2)


def test_execute_batch_success_callback_receives_return_types():
    client = GraphClient()
    request = client.pending_request()
    request.beforeExecute.clear()
    request.authenticate_request = lambda _request: None
    obj = ClientObject(client, ResourcePath("me"))
    client.add_query(ReadEntityQuery(obj, ["displayName"]))
    client.add_query(ClientQuery(client))
    received: list = []
    transport = _FakeTransport([_envelope([200, 200])])

    def _factory(*args, **kwargs):
        batch_request = ODataV4BatchRequest(*args, **kwargs)
        batch_request.transport = transport
        return batch_request

    with mock.patch("office365.graph_client.ODataV4BatchRequest", side_effect=_factory):
        client.execute_batch(success_callback=received.append)

    assert received == [[obj]]


# ── Async batch (true-async twin of execute_query_with_retry) ────────────────


class _ResponseTransport(BaseTransport):
    """Returns pre-built ``Response`` objects in order (sync execute; async offloads)."""

    def __init__(self, responses: list[Response]) -> None:
        self._responses = responses
        self.calls = 0

    def execute(self, request):
        resp = self._responses[min(self.calls, len(self._responses) - 1)]
        self.calls += 1
        return resp


class _RejectThenOkTransport(BaseTransport):
    """Whole-batch rejection (413) on the first call, a 200 envelope afterwards."""

    def __init__(self) -> None:
        self.calls = 0

    def execute(self, request):
        self.calls += 1
        resp = Response()
        resp.url = request.url
        if self.calls == 1:
            resp.status_code = 413
            resp._content = b"payload too large"
        else:
            resp.status_code = 200
            resp._content = jsonlib.dumps(_envelope([200])).encode("utf-8")
        return resp


def _v3_batch_response(sub_statuses: list[int], retry_after: int | None = None) -> Response:
    """Build a multipart/mixed v3 batch response with the given sub-statuses."""
    boundary = "batch_response"
    parts = []
    for status in sub_statuses:
        if status == 429:  # noqa: PLR2004
            inner = f"HTTP/1.1 429 Too Many Requests\r\nRetry-After: {retry_after or 1}\r\n"
        elif status == 200:  # noqa: PLR2004
            inner = "HTTP/1.1 200 OK\r\nContent-Type: application/json\r\n\r\n" + jsonlib.dumps({"d": {}})
        else:
            body = jsonlib.dumps({"error": {"code": "Denied", "message": "access denied"}})
            inner = f"HTTP/1.1 {status} Sub Request Failed\r\nContent-Type: application/json\r\n\r\n{body}"
        parts.append(
            f"--{boundary}\r\nContent-Type: application/http\r\nContent-Transfer-Encoding: binary\r\n\r\n{inner}\r\n"
        )
    body = "".join(parts) + f"--{boundary}--\r\n"
    resp = Response()
    resp.status_code = 200
    resp.url = "https://contoso.sharepoint.com/_api/$batch"
    resp.headers["Content-Type"] = f"multipart/mixed; boundary={boundary}"
    resp._content = body.encode("utf-8")
    return resp


class TestBatchSubRequestRetryAsync(unittest.TestCase):
    def test_async_retries_only_failed_subrequests(self):
        client = GraphClient()
        transport = _FakeTransport([_envelope([200, 429], retry_after=1), _envelope([200])])
        req = ODataV4BatchRequest("", V4JsonFormat())
        req.transport = transport

        with mock.patch("office365.runtime.retry.asyncio.sleep", new=mock.AsyncMock()):
            asyncio.run(
                req.execute_query_with_retry_async(_make_batch(client, 2), max_retry=3, base_delay=1, jitter=False)
            )

        self.assertEqual(transport.calls, 2)
        self.assertEqual(len(transport.request_payloads[0]["requests"]), 2)
        self.assertEqual(len(transport.request_payloads[1]["requests"]), 1)

    def test_async_non_transient_sub_failure_raises_without_retry(self):
        client = GraphClient()
        transport = _FakeTransport([_envelope([200, 400])])
        req = ODataV4BatchRequest("", V4JsonFormat())
        req.transport = transport

        with self.assertRaises(ClientRequestException):
            asyncio.run(req.execute_query_with_retry_async(_make_batch(client, 2), max_retry=3))

        self.assertEqual(transport.calls, 1)

    def test_async_honors_longest_retry_after(self):
        client = GraphClient()
        transport = _FakeTransport([_envelope([429, 429], retry_after=7), _envelope([200, 200])])
        req = ODataV4BatchRequest("", V4JsonFormat())
        req.transport = transport
        sleep_mock = mock.AsyncMock()

        with mock.patch("office365.runtime.retry.asyncio.sleep", new=sleep_mock):
            asyncio.run(req.execute_query_with_retry_async(_make_batch(client, 2), max_retry=3, jitter=False))

        sleep_mock.assert_awaited_once_with(7)

    def test_async_splits_whole_batch_rejection(self):
        client = GraphClient()
        transport = _RejectThenOkTransport()
        req = ODataV4BatchRequest("", V4JsonFormat())
        req.transport = transport

        with mock.patch("office365.runtime.retry.asyncio.sleep", new=mock.AsyncMock()):
            asyncio.run(
                req.execute_query_with_retry_async(_make_batch(client, 2), max_retry=1, base_delay=1, jitter=False)
            )

        self.assertEqual(transport.calls, 3)

    def test_v3_async_retries_only_failed_subrequests(self):
        client = GraphClient()
        client.pending_request().beforeExecute.clear()  # no auth handler during offline payload build
        obj1 = ClientObject(client, ResourcePath("me"))
        obj2 = ClientObject(client, ResourcePath("me"))
        batch = BatchQuery(client, [ReadEntityQuery(obj1, ["a"]), ReadEntityQuery(obj2, ["b"])])
        transport = _ResponseTransport([_v3_batch_response([200, 429], retry_after=1), _v3_batch_response([200])])
        req = ODataBatchV3Request("https://contoso.sharepoint.com", JsonLightFormat())
        req.transport = transport

        with mock.patch("office365.runtime.retry.asyncio.sleep", new=mock.AsyncMock()):
            asyncio.run(req.execute_query_with_retry_async(batch, max_retry=3, base_delay=1, jitter=False))

        self.assertEqual(transport.calls, 2)


# ── SharePoint batch rounds: per-query handlers, deferred barriers, draining ──


_DOCLIB_LIST_ID = "6f0a1b2c-3d4e-5f60-7182-93a4b5c6d7e8"
_DOCLIB_URL = "/sites/dev/Shared Documents"

_FOLDER_BODY = {
    "d": {
        "__metadata": {"type": "SP.Folder"},
        "UniqueId": "11111111-2222-3333-4444-555555555555",
        "ServerRelativeUrl": _DOCLIB_URL,
        "Properties": {"vti_x005f_listname": _DOCLIB_LIST_ID},
    }
}
_LIST_BODY = {"d": {"__metadata": {"type": "SP.List"}, "Title": "Shared Documents"}}
_CREATE_BODY = {"d": {"__metadata": {"type": "SP.Folder"}, "ServerRelativeUrl": _DOCLIB_URL + "/A1"}}


async def _noop_async() -> None:
    pass


def _v3_response_with_bodies(bodies: list[dict]) -> Response:
    """Build a multipart/mixed v3 batch response carrying the given JSON bodies."""
    boundary = "batch_response"
    parts = []
    for body in bodies:
        inner = "HTTP/1.1 200 OK\r\nContent-Type: application/json\r\n\r\n" + jsonlib.dumps(body)
        parts.append(
            f"--{boundary}\r\nContent-Type: application/http\r\nContent-Transfer-Encoding: binary\r\n\r\n{inner}\r\n"
        )
    raw = "".join(parts) + f"--{boundary}--\r\n"
    resp = Response()
    resp.status_code = 200
    resp.url = "https://contoso.sharepoint.com/_api/$batch"
    resp.headers["Content-Type"] = f"multipart/mixed; boundary={boundary}"
    resp._content = raw.encode("utf-8")
    return resp


class _ScriptedBatchTransport(BaseTransport):
    """Records batch rounds and standalone requests, replaying scripted JSON."""

    def __init__(self, bodies_per_round: list[list[dict]], single_bodies: list[dict] | None = None) -> None:
        self._bodies = bodies_per_round
        self._single_bodies = single_bodies or []
        self.rounds: list[list[str]] = []
        self.payloads: list[str] = []
        self.singles: list[str] = []
        self.single_payloads: list[str] = []

    def execute(self, request):
        if "$batch" in request.url:
            payload = request.data
            if isinstance(payload, bytes):
                payload = payload.decode("utf-8", "replace")
            self.payloads.append(payload)
            lines = [
                line.strip()
                for line in payload.splitlines()
                if line.startswith(("GET ", "POST ", "PATCH ", "MERGE ", "DELETE "))
            ]
            self.rounds.append(lines)
            index = min(len(self.rounds) - 1, len(self._bodies) - 1)
            return _v3_response_with_bodies(self._bodies[index])

        self.singles.append(f"{request.method} {request.url} HTTP/1.1")
        data = request.data
        self.single_payloads.append(data.decode("utf-8", "replace") if isinstance(data, bytes) else (data or ""))
        index = min(len(self.singles) - 1, len(self._single_bodies) - 1)
        body = self._single_bodies[index] if self._single_bodies else {"d": {}}
        resp = Response()
        resp.status_code = 200
        resp.url = request.url
        resp.headers["Content-Type"] = "application/json;odata=verbose"
        resp._content = jsonlib.dumps(body).encode("utf-8")
        return resp

    def reset_connections(self) -> None:  # pragma: no cover - transport hygiene no-op
        pass


def _sharepoint_ctx(transport: _ScriptedBatchTransport) -> ClientContext:
    """ClientContext whose auth/digest round-trips are stubbed for offline batches."""
    ctx = ClientContext("https://contoso.sharepoint.com")
    request = ctx.pending_request()
    request.beforeExecute.clear()  # drop the auth handler; per-query handlers stay
    request.warm_up = lambda: None
    request.warm_up_async = _noop_async
    request.ensure_form_digest = lambda *args, **kwargs: None
    request._authenticate_request = lambda *args, **kwargs: None
    request.transport = transport
    return ctx


def test_batch_applies_per_query_before_execute_handler():
    """A sub-query's ``before_execute`` mutation is honored during payload build."""
    transport = _ScriptedBatchTransport([[_FOLDER_BODY]])
    ctx = _sharepoint_ctx(transport)
    qry = ClientQuery(ctx)

    def _construct(request):
        request.url = "https://contoso.sharepoint.com/_api/custom"

    ctx.add_query(qry).before_execute(_construct)
    ctx.execute_batch()

    assert transport.rounds == [["GET https://contoso.sharepoint.com/_api/custom HTTP/1.1"]]


def test_batch_fires_per_query_after_execute_handler():
    """A sub-query's ``after_execute`` handler runs as its sub-response is applied."""
    transport = _ScriptedBatchTransport([[_FOLDER_BODY, _FOLDER_BODY]])
    ctx = _sharepoint_ctx(transport)
    ctx.add_query(ClientQuery(ctx))
    fired: list[object] = []
    ctx.load(ctx.web).after_execute(lambda _: fired.append(True))

    ctx.execute_batch()

    assert fired == [True]


def test_independent_queries_execute_in_a_single_round():
    """The drain loop must not add rounds when nothing enqueues follow-ups."""
    transport = _ScriptedBatchTransport([[_FOLDER_BODY, _FOLDER_BODY, _FOLDER_BODY]])
    ctx = _sharepoint_ctx(transport)
    for _ in range(3):
        ctx.load(ctx.web)

    ctx.execute_batch(3)

    assert len(transport.rounds) == 1


def test_non_batchable_query_is_flushed_in_order():
    """A non-batchable query splits the round: batch, standalone, then batch."""
    transport = _ScriptedBatchTransport([[_FOLDER_BODY], [_FOLDER_BODY]])
    ctx = _sharepoint_ctx(transport)
    ctx.load(ctx.web)
    single = ClientQuery(ctx)
    single.batchable = False

    def _construct(request):
        request.url = "https://contoso.sharepoint.com/_api/standalone"

    ctx.add_query(single).before_execute(_construct)
    ctx.load(ctx.web)

    ctx.execute_batch()

    assert [round_[0].split()[0] for round_ in transport.rounds] == ["GET", "GET"]
    assert transport.singles == ["GET https://contoso.sharepoint.com/_api/standalone HTTP/1.1"]


def test_document_set_create_drains_all_rounds():
    """#868: the multi-phase ``DocumentSet.create`` chain materializes under batch."""
    transport = _ScriptedBatchTransport([[_FOLDER_BODY], [_LIST_BODY]], single_bodies=[_CREATE_BODY])
    ctx = _sharepoint_ctx(transport)
    parent = ctx.web.get_folder_by_server_relative_url(_DOCLIB_URL)

    created = DocumentSet.create(ctx, parent, "A1")
    ctx.execute_batch(3)

    assert len(transport.rounds) == 2, transport.rounds  # noqa: PLR2004
    assert transport.rounds[0][0].startswith("GET ")
    assert transport.rounds[1][0].startswith("GET ")
    # ``listdata.svc`` isn't accepted inside ``/_api/$batch`` -> run standalone
    assert transport.singles == ["POST https://contoso.sharepoint.com/_vti_bin/listdata.svc/SharedDocuments HTTP/1.1"]
    assert created.get_property("ServerRelativeUrl") == _DOCLIB_URL + "/A1"


def test_document_set_create_resolves_deferred_barrier():
    """Cached prerequisites queue a barrier; resolving it must drive the chain."""
    transport = _ScriptedBatchTransport([[_LIST_BODY]], single_bodies=[_CREATE_BODY])
    ctx = _sharepoint_ctx(transport)
    parent = ctx.web.get_folder_by_server_relative_url(_DOCLIB_URL)
    parent.set_property("UniqueId", "11111111-2222-3333-4444-555555555555")
    parent.set_property("ServerRelativeUrl", _DOCLIB_URL)
    parent.set_property("Properties", {"vti_x005f_listname": _DOCLIB_LIST_ID})

    DocumentSet.create(ctx, parent, "A1")
    ctx.execute_batch(3)

    assert len(transport.rounds) == 1, transport.rounds
    assert transport.rounds[0][0].startswith("GET ")
    assert transport.singles == ["POST https://contoso.sharepoint.com/_vti_bin/listdata.svc/SharedDocuments HTTP/1.1"]


# ── #717: list item entity type must be resolved before the create round ──────

_LIST_TYPE_BODY = {
    "d": {
        "__metadata": {"type": "SP.List"},
        "ListItemEntityTypeFullName": "SP.Data.MyListListItem",
    }
}


def test_batched_update_body_matches_the_standalone_body():
    """#943: an item update serializes identically inside and outside a change set.

    A hyperlink column written as a plain ``{"Url": ..., "Description": ...}`` dict
    carries no type of its own, so the sub-request must still annotate the item
    (``SP.Data.<List>ListItem``) exactly as the standalone request does. Without it
    the server answered ``A value without a type name was found`` and rejected the
    whole change set — after the first item had already been written.
    """
    list_body = {"d": {"Id": 10, "ListItemEntityTypeFullName": "SP.Data.MyListListItem"}}

    def _update_item(ctx: ClientContext) -> None:
        lst = ctx.web.lists.get_by_title("MyList")
        lst.set_property("Id", "11111111-2222-3333-4444-555555555555")
        item = lst.items.get_by_id(10)
        item.set_property("Link", {"Url": "https://contoso.com/x", "Description": "X"}).update()

    def _body(payload) -> str:
        return jsonlib.dumps(payload) if isinstance(payload, dict) else payload

    single = _ScriptedBatchTransport([[list_body]], single_bodies=[list_body])
    single_ctx = _sharepoint_ctx(single)
    _update_item(single_ctx)
    single_ctx.execute_query()
    standalone_body = next(_body(payload) for payload in single.single_payloads if '"Link"' in _body(payload))

    batched = _ScriptedBatchTransport([[list_body]], single_bodies=[list_body])
    ctx = _sharepoint_ctx(batched)
    _update_item(ctx)
    ctx.execute_batch()

    assert '"SP.Data.MyListListItem"' in standalone_body
    # The type read is its own round, and the MERGE carries the same body the
    # standalone request sent — the annotation is adopted before serialization.
    assert [[line.split()[0] for line in rnd] for rnd in batched.rounds] == [["GET"], ["MERGE"]]
    assert standalone_body in batched.payloads[-1]


def test_add_item_resolves_entity_type_before_create_round():
    """#717: the create must not be batched with the list's type-name read.

    The annotation (``SP.Data.<List>ListItem``) is read in one round, then the POST
    is serialized in a later round; otherwise the server sees a multi-lookup value
    collection on an ``SP.ListItem`` and rejects it as an open collection.
    """
    transport = _ScriptedBatchTransport([[_LIST_TYPE_BODY], [{"d": {}}]])
    ctx = _sharepoint_ctx(transport)
    lst = ctx.web.lists.get_by_title("MyList")

    item = lst.add_item({"Title": "A1"})
    ctx.execute_batch()

    assert len(transport.rounds) == 2, transport.rounds  # noqa: PLR2004
    assert transport.rounds[0][0].startswith("GET ")
    assert transport.rounds[1][0].startswith("POST ")
    assert "/items" in transport.rounds[1][0]
    assert item.entity_type_name == "SP.Data.MyListListItem"
    assert "SP.Data.MyListListItem" in transport.payloads[1]


def test_add_item_reuses_cached_entity_type_without_reading_it_again():
    """Once cached, the type annotation is adopted without an extra list read."""
    transport = _ScriptedBatchTransport([[{"d": {}}]])
    ctx = _sharepoint_ctx(transport)
    lst = ctx.web.lists.get_by_title("MyList")
    lst.set_property("Id", "11111111-2222-3333-4444-555555555555")
    lst.set_property("ListItemEntityTypeFullName", "SP.Data.MyListListItem")

    item = lst.add_item({"Title": "A1"})
    ctx.execute_batch()

    assert len(transport.rounds) == 1, transport.rounds
    assert transport.rounds[0][0].startswith("POST ")
    assert item.entity_type_name == "SP.Data.MyListListItem"
    assert "SP.Data.MyListListItem" in transport.payloads[0]


def test_queue_records_resolves_entity_type_before_create_round():
    """Bulk record creates must adopt the list's entity type too.

    A collection-valued column (multi-lookup/person) needs the typed annotation so
    the server can resolve it; without it the ``$batch`` entry is rejected as an
    untyped value. ``queue_records`` is the bulk sibling of ``add_item``.
    """
    transport = _ScriptedBatchTransport([[_LIST_TYPE_BODY], [{"d": {}}]])
    ctx = _sharepoint_ctx(transport)
    lst = ctx.web.lists.get_by_title("MyList")

    lst.items.queue_records([{"Title": "A1"}])
    ctx.execute_batch()

    assert len(transport.rounds) == 2, transport.rounds  # noqa: PLR2004
    assert transport.rounds[0][0].startswith("GET ")
    assert transport.rounds[1][0].startswith("POST ")
    assert "SP.Data.MyListListItem" in transport.payloads[1]


def test_document_set_create_drains_all_rounds_async():
    """Async twin of the multi-phase ``DocumentSet.create`` batch chain."""
    transport = _ScriptedBatchTransport([[_FOLDER_BODY], [_LIST_BODY]], single_bodies=[_CREATE_BODY])
    ctx = _sharepoint_ctx(transport)
    parent = ctx.web.get_folder_by_server_relative_url(_DOCLIB_URL)

    DocumentSet.create(ctx, parent, "A1")
    asyncio.run(ctx.execute_batch_async(3))

    assert len(transport.rounds) == 2, transport.rounds  # noqa: PLR2004
    assert transport.singles == ["POST https://contoso.sharepoint.com/_vti_bin/listdata.svc/SharedDocuments HTTP/1.1"]


# ── Tolerant batches: record a rejected sub-request instead of aborting ───────


def _graph_batch(client: GraphClient, count: int) -> BatchQuery:
    client.pending_request().beforeExecute.clear()
    return BatchQuery(client, [ClientQuery(client) for _ in range(count)])


class TestTolerantBatch(unittest.TestCase):
    def test_records_rejected_subrequest_and_applies_the_rest(self):
        client = GraphClient()
        transport = _FakeTransport([_envelope([200, 400])])
        req = ODataV4BatchRequest("", V4JsonFormat())
        req.transport = transport
        batch = _graph_batch(client, 2)

        with client.collect_batch_failures() as failures:
            req.execute_query_with_retry(batch, max_retry=3)

        self.assertEqual(len(failures), 1)
        self.assertIs(failures[0][0], batch.queries[1])
        self.assertEqual(failures[0][1].response.status_code, 400)  # noqa: PLR2004
        self.assertEqual(transport.calls, 1)  # a permanent failure is not retried

    def test_default_semantics_return_outside_the_scope(self):
        client = GraphClient()
        req = ODataV4BatchRequest("", V4JsonFormat())
        req.transport = _FakeTransport([_envelope([400])])

        with self.assertRaises(ClientRequestException):
            req.execute_query_with_retry(_graph_batch(client, 1), max_retry=1)

        with client.collect_batch_failures():
            pass

        self.assertFalse(client.collecting_batch_failures)
        with self.assertRaises(ClientRequestException):
            req.execute_query_with_retry(_graph_batch(client, 1), max_retry=1)

    def test_records_subrequests_still_failing_after_retries(self):
        client = GraphClient()
        req = ODataV4BatchRequest("", V4JsonFormat())
        req.transport = _FakeTransport([_envelope([429], retry_after=1)])

        with mock.patch("office365.runtime.retry.sleep"):
            with client.collect_batch_failures() as failures:
                req.execute_query_with_retry(_graph_batch(client, 1), max_retry=2, base_delay=1, jitter=False)

        self.assertEqual(len(failures), 1)
        self.assertEqual(failures[0][1].response.status_code, 429)  # noqa: PLR2004

    def test_tolerant_async_twin(self):
        client = GraphClient()
        req = ODataV4BatchRequest("", V4JsonFormat())
        req.transport = _FakeTransport([_envelope([200, 403])])
        batch = _graph_batch(client, 2)

        async def _run() -> list:
            with client.collect_batch_failures() as failures:
                await req.execute_query_with_retry_async(batch, max_retry=2)
            return failures

        failures = asyncio.run(_run())

        self.assertEqual(len(failures), 1)
        self.assertIs(failures[0][0], batch.queries[1])

    def test_records_a_single_request_still_rejected_whole(self):
        ctx = ClientContext("https://contoso.sharepoint.com")
        ctx.pending_request().beforeExecute.clear()  # no auth/digest handler offline

        class _AlwaysRejected(BaseTransport):
            calls = 0

            def execute(self, request):
                self.calls += 1
                resp = Response()
                resp.url = request.url
                resp.status_code = 413
                resp._content = b"payload too large"
                return resp

        transport = _AlwaysRejected()
        req = ODataBatchV3Request("https://contoso.sharepoint.com", JsonLightFormat(), transport=transport)
        batch = BatchQuery(ctx, [ClientQuery(ctx)])

        with ctx.collect_batch_failures() as failures:
            req.execute_query_with_retry(batch, max_retry=1)

        self.assertEqual(transport.calls, 1)
        self.assertEqual(len(failures), 1)
        self.assertIs(failures[0][0], batch.queries[0])
        self.assertIn("batch of 1 was still rejected", str(failures[0][1]))

    def test_v3_records_rejected_subrequest(self):
        ctx = ClientContext("https://contoso.sharepoint.com")
        ctx.pending_request().beforeExecute.clear()  # no auth/digest handler offline
        obj1 = ClientObject(ctx, ResourcePath("me"))
        obj2 = ClientObject(ctx, ResourcePath("me"))
        batch = BatchQuery(ctx, [ReadEntityQuery(obj1, ["a"]), ReadEntityQuery(obj2, ["b"])])
        req = ODataBatchV3Request(
            "https://contoso.sharepoint.com",
            JsonLightFormat(),
            transport=_ResponseTransport([_v3_batch_response([200, 403])]),
        )

        with ctx.collect_batch_failures() as failures:
            req.execute_query_with_retry(batch, max_retry=1)

        self.assertEqual(len(failures), 1)
        self.assertIs(failures[0][0], batch.queries[1])
        self.assertEqual(failures[0][1].response.status_code, 403)  # noqa: PLR2004

    def test_v3_async_records_rejected_subrequest(self):
        ctx = ClientContext("https://contoso.sharepoint.com")
        ctx.pending_request().beforeExecute.clear()  # no auth/digest handler offline
        batch = BatchQuery(ctx, [ClientQuery(ctx), ClientQuery(ctx)])
        req = ODataBatchV3Request(
            "https://contoso.sharepoint.com",
            JsonLightFormat(),
            transport=_ResponseTransport([_v3_batch_response([403])]),
        )

        async def _run() -> list:
            with ctx.collect_batch_failures() as failures:
                await req.execute_query_with_retry_async(batch, max_retry=1)
            return failures

        failures = asyncio.run(_run())

        self.assertEqual(len(failures), 1)
        self.assertIs(failures[0][0], batch.queries[0])

    def test_nested_scope_is_rejected(self):
        ctx = ClientContext("https://contoso.sharepoint.com")
        with ctx.collect_batch_failures():
            self.assertTrue(ctx.collecting_batch_failures)
            with self.assertRaises(RuntimeError):
                with ctx.collect_batch_failures():
                    pass
        self.assertFalse(ctx.collecting_batch_failures)
