"""Offline tests for the ``Entity.update_properties`` write helper.

``update_properties(**values)`` is sugar over repeated ``set_property`` calls
plus a single queued ``update()``: it coerces values the same way, stays
deferred until ``execute_query()`` and works for both the Graph and SharePoint
entity bases.
"""

from __future__ import annotations

import pytest
from office365.graph_client import GraphClient
from office365.runtime.http.http_method import HttpMethod
from office365.sharepoint.client_context import ClientContext
from tests import test_site_url
from tests._scripted_transport import ScriptedTransport


class _RecordingTransport(ScriptedTransport):
    """Scripted transport that also records the requests it received."""

    def __init__(self, payloads):
        super().__init__(payloads)
        self.requests = []

    def execute(self, request):
        self.requests.append(request)
        return super().execute(request)


def _graph(payloads):
    client = GraphClient()
    client.pending_request().beforeExecute.clear()
    transport = _RecordingTransport(payloads)
    client.pending_request().transport = transport
    return client, transport


def _sp(payloads):
    ctx = ClientContext(test_site_url)
    ctx.pending_request().beforeExecute.clear()
    transport = _RecordingTransport(payloads)
    ctx.pending_request().transport = transport
    return ctx, transport


def _graph_user(payloads):
    client, transport = _graph(payloads)
    return client, transport, client.users["jdoe@contoso.com"]


def _sp_web(payloads):
    ctx, transport = _sp(payloads)
    return ctx, transport, ctx.web


# --- deferred, single request -------------------------------------------------


@pytest.mark.parametrize(
    ("factory", "payloads", "values", "method", "header", "url_suffix"),
    [
        (
            _graph_user,
            [{"id": "1"}],
            {"displayName": "John Doe", "jobTitle": "Engineer"},
            HttpMethod.Patch,
            None,
            None,
        ),
        (
            _sp_web,
            [{"d": {}}],
            {"Title": "Contoso", "Description": "Team site"},
            HttpMethod.Post,
            "MERGE",
            "/Web",
        ),
    ],
)
def test_update_properties_sends_a_single_request(factory, payloads, values, method, header, url_suffix):
    _context, transport, entity = factory(payloads)

    entity.update_properties(**values).execute_query()

    assert transport.calls == 1
    request = transport.requests[0]
    assert request.method == method
    if header is not None:
        assert request.headers.get("X-HTTP-Method") == header
    if url_suffix is not None:
        assert request.url.endswith(url_suffix)
    for name, value in values.items():
        assert request.data[name] == value
