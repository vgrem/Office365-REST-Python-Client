"""Tests for per-request ``client-request-id`` telemetry (C4)."""

from __future__ import annotations

import asyncio
import uuid
from typing import Any

import requests
from office365.graph_client import GraphClient
from office365.runtime.odata.v3.batch_request import ODataBatchV3Request
from office365.runtime.odata.v3.json_light_format import JsonLightFormat
from office365.runtime.odata.v4.batch_request import ODataV4BatchRequest
from office365.runtime.odata.v4.json_format import V4JsonFormat
from office365.runtime.queries.batch import BatchQuery
from office365.runtime.queries.client_query import ClientQuery
from office365.runtime.transport.requests_transport import RequestsTransport
from office365.sharepoint.client_context import ClientContext
from requests import Response

_HEADER = "client-request-id"


class _RecordingSession(requests.Session):
    """A ``Session`` that records the kwargs of every dispatched request."""

    def __init__(self) -> None:
        super().__init__()
        self.calls: list[tuple[str, str, dict[str, Any]]] = []

    def request(self, method: str, url: str, **kwargs: Any) -> Response:  # type: ignore[override]
        self.calls.append((method, url, kwargs))
        response = Response()
        response.status_code = 200
        response.url = url
        response._content = b'{"d": {"Title": "Contoso"}}'
        response._content_consumed = True
        return response


def _context() -> tuple[ClientContext, _RecordingSession]:
    ctx = ClientContext("https://contoso.sharepoint.com")
    ctx.pending_request().beforeExecute.clear()  # no auth/digest handler offline
    session = _RecordingSession()
    ctx.pending_request().transport = RequestsTransport(session=session)
    ctx.load(ctx.web)
    return ctx, session


def _assert_guid(value: str) -> None:
    parsed = uuid.UUID(value)
    assert str(parsed) == value.lower()


def test_user_supplied_client_request_id_wins() -> None:
    ctx, session = _context()
    ctx.pending_request().before_execute(lambda request: request.set_header(_HEADER, "caller-id"), once=True)

    ctx.execute_query()

    assert session.calls[0][2]["headers"][_HEADER] == "caller-id"


def test_client_request_id_sent_on_async_path() -> None:
    ctx, session = _context()

    asyncio.run(ctx.execute_query_async())

    _assert_guid(session.calls[0][2]["headers"][_HEADER])


def _payload_requests(payload: dict) -> list[dict]:
    return payload["requests"]


def test_batch_subrequests_respect_opt_out() -> None:
    client = GraphClient()
    client.pending_request().beforeExecute.clear()
    client.with_client_request_id(False)
    batch = BatchQuery(client, [ClientQuery(client) for _ in range(2)])

    payload = ODataV4BatchRequest("", V4JsonFormat())._prepare_payload(batch)

    assert all(_HEADER not in item["headers"] for item in _payload_requests(payload))


def test_v3_batch_subrequests_embed_ids() -> None:
    ctx = ClientContext("https://contoso.sharepoint.com")
    ctx.pending_request().beforeExecute.clear()
    batch = BatchQuery(ctx, [ClientQuery(ctx) for _ in range(2)])

    body = ODataBatchV3Request("https://contoso.sharepoint.com", JsonLightFormat())._prepare_payload(batch)

    assert body.count(b"client-request-id:") == 2  # noqa: PLR2004
