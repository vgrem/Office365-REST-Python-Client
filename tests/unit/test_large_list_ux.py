"""Unit tests for the large-list UX: truncation warning, index candidates, pre-flight."""

from __future__ import annotations

import warnings

from office365.runtime.client_object_collection import ClientObjectCollection
from office365.runtime.paths.resource_path import ResourcePath
from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.exceptions import SPQueryThrottledException
from office365.sharepoint.fields.field import Field
from office365.sharepoint.listitems.caml import CamlQuery
from tests import test_site_url
from tests._scripted_transport import ScriptedTransport


class _ThresholdCollection(ClientObjectCollection):
    _list_view_threshold = 3
    _truncation_hint = "page it"


def _collection() -> _ThresholdCollection:
    return _ThresholdCollection(ClientContext(test_site_url), Field, ResourcePath("x"))


def test_unpaged_collection_warns_once_at_threshold():
    col = _collection()
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        for _ in range(3):
            col.add_child(Field(col.context))
    assert len([w for w in caught if issubclass(w.category, UserWarning)]) == 1


def _context(payloads: list) -> tuple[ClientContext, ScriptedTransport]:
    ctx = ClientContext(test_site_url)
    ctx.pending_request().beforeExecute.clear()
    transport = ScriptedTransport(payloads)
    ctx.pending_request().transport = transport
    return ctx, transport


def test_check_query_raises_for_non_indexed_column():
    ctx, _ = _context(
        [
            {"d": {"ItemCount": 6000}},
            {"d": {"results": [{"InternalName": "date", "Title": "date", "Indexed": False}]}},
        ]
    )
    lst = ctx.web.lists.get_by_title("X")
    query = CamlQuery.builder().order_by("date").build()

    try:
        lst.check_query(query)
    except SPQueryThrottledException as exc:
        assert "date" in str(exc)
    else:
        raise AssertionError("expected SPQueryThrottledException")
