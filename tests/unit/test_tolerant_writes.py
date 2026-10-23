"""Offline tests for the tolerant write helpers.

``ignore_missing=True`` makes ``delete_object`` / ``recycle`` idempotent: an
HTTP 404 is treated as success, while every other failure still propagates.
``ViewCollection.ensure_view`` is a deferred get-or-create.
"""

from __future__ import annotations

import pytest
from office365.graph_client import GraphClient
from office365.runtime.client_request_exception import ClientRequestException
from office365.runtime.exceptions import ObjectNotFoundException
from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.views.view import View
from tests import test_site_url
from tests._scripted_transport import ScriptedTransport

_NOT_FOUND = {
    "http_status": 404,
    "body": {"error": {"code": "Request_ResourceNotFound", "message": "Resource not found"}},
}

_FORBIDDEN = {
    "http_status": 403,
    "body": {"error": {"code": "Forbidden", "message": "Access is denied."}},
}


class _RecordingTransport(ScriptedTransport):
    """Scripted transport that also records the requests it received."""

    def __init__(self, payloads):
        super().__init__(payloads)
        self.requests = []

    def execute(self, request):
        self.requests.append(request)
        return super().execute(request)


def _graph(payloads):
    transport = _RecordingTransport(payloads)
    client = GraphClient()
    client.pending_request().beforeExecute.clear()
    client.pending_request().transport = transport
    return client, transport


def _sp(payloads):
    ctx = ClientContext(test_site_url)
    ctx.pending_request().beforeExecute.clear()
    transport = _RecordingTransport(payloads)
    ctx.pending_request().transport = transport
    return ctx, transport


# --- delete_object(ignore_missing=...) ---------------------------------------


def test_graph_delete_object_raises_when_missing_by_default():
    client, transport = _graph([_NOT_FOUND])

    with pytest.raises(ObjectNotFoundException):
        client.users["missing@contoso.com"].delete_object().execute_query()

    assert transport.calls == 1


def test_graph_delete_object_propagates_non_404_even_with_ignore_missing():
    client, _ = _graph([_FORBIDDEN])

    with pytest.raises(ClientRequestException):
        client.users["x@contoso.com"].delete_object(ignore_missing=True).execute_query()


def test_sharepoint_delete_object_tolerates_missing():
    ctx, transport = _sp([_NOT_FOUND])

    ctx.web.lists.get_by_title("Documents").delete_object(ignore_missing=True).execute_query()

    assert transport.calls == 1


def test_sharepoint_folder_recycle_tolerates_missing():
    ctx, transport = _sp([_NOT_FOUND])

    ctx.web.get_folder_by_server_relative_path("/sites/x/Shared Documents/sub").recycle(
        ignore_missing=True
    ).execute_query()

    assert transport.calls == 1


# --- ViewCollection.ensure_view ----------------------------------------------


def _views(ctx):
    return ctx.web.lists.get_by_title("Documents").views


def test_ensure_view_creates_when_missing():
    ctx, transport = _sp([_NOT_FOUND, {"d": {"Id": "v1", "Title": "Active"}}])

    view = _views(ctx).ensure_view("Active", fields=["Title"]).execute_query()

    assert transport.calls == 2  # noqa: PLR2004
    assert isinstance(view, View)
    assert view.title == "Active"
    assert view.id == "v1"
    # the second request is the Add; the created view stays addressable by title
    assert "GetByTitle" in str(view.resource_path)


def test_ensure_view_on_conflict_update_reconciles_scalar_settings():
    ctx, transport = _sp(
        [
            {"d": {"Id": "v1", "Title": "Active", "RowLimit": 30}},
            {},
        ]
    )

    view = _views(ctx).ensure_view("Active", row_limit=50, on_conflict="update").execute_query()

    assert transport.calls == 2  # noqa: PLR2004
    assert view.row_limit == 50  # noqa: PLR2004
