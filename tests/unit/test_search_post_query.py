"""Offline tests for the POST form of a search query.

``SearchService.post_query`` sends a ``SearchRequest`` body rather than a query
string, so a caller asking for a sort specification has to spell it the way the
request schema does (``SortList``) even though the GET form calls the same thing
``sortList``. These tests pin the wire shape of that body: the sorting travels
inside ``request`` and a caller that asks for no sorting sends no sort entries.
"""

from __future__ import annotations

from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.search.query.sort.sort import Sort
from tests import test_site_url
from tests._scripted_transport import RoutingTransport


def _ctx() -> tuple[ClientContext, RoutingTransport]:
    transport = RoutingTransport([("postquery", {})])
    ctx = ClientContext(test_site_url)
    request = ctx.pending_request()
    request.beforeExecute.clear()
    request.transport = transport
    return ctx, transport


def _request_body(transport: RoutingTransport) -> dict:
    return transport.requests[0].data["request"]


def test_post_query_carries_a_sort_list():
    ctx, transport = _ctx()

    ctx.search.post_query(
        "contoso",
        select_properties=["Title"],
        trim_duplicates=True,
        row_limit=10,
        enable_sorting=True,
        sort_list=[Sort(Direction=0, Property="Modified")],
    ).execute_query()

    body = _request_body(transport)
    assert body["EnableSorting"] is True
    assert body["SortList"]["results"] == [{"Direction": 0, "Property": "Modified"}]
    assert transport.calls[0].endswith("SearchService/postquery")


def test_post_query_without_a_sort_list_sends_none():
    ctx, transport = _ctx()

    ctx.search.post_query("contoso").execute_query()

    body = _request_body(transport)
    # an empty collection is not serialized, so existing callers see the same body
    assert "SortList" not in body
    assert "EnableSorting" not in body
