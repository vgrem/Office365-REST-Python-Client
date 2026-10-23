"""Offline tests for the SharePoint bulk collection write helpers.

``EntityCollection.update_all`` and ``EntityCollection.delete_all`` queue one
update/delete per loaded entity; running the queue with ``execute_batch`` sends
the writes as a handful of ``$batch`` requests. The collection must be loaded
first — only the entities already loaded are touched.
"""

from __future__ import annotations

import pytest
from office365.runtime.exceptions import ObjectNotFoundException
from office365.sharepoint.client_context import ClientContext
from tests import test_site_url
from tests._scripted_transport import ScriptedTransport

_NOT_FOUND = {
    "http_status": 404,
    "body": {"error": {"code": "Request_ResourceNotFound", "message": "Resource not found"}},
}


class _RecordingTransport(ScriptedTransport):
    """Scripted transport that also records the requests it received."""

    def __init__(self, payloads):
        super().__init__(payloads)
        self.requests = []

    def execute(self, request):
        self.requests.append(request)
        return super().execute(request)


def _sp(payloads):
    ctx = ClientContext(test_site_url)
    ctx.pending_request().beforeExecute.clear()
    transport = _RecordingTransport(payloads)
    ctx.pending_request().transport = transport
    return ctx, transport


def _loaded(ctx, *titles):
    """Build a views collection whose entities are already loaded (offline)."""
    collection = ctx.web.lists.get_by_title("Documents").views
    for index, title in enumerate(titles, 1):
        view = collection.create_typed_object()
        for name, value in (("Id", f"v{index}"), ("Title", title)):
            view.set_property(name, value, False)
        collection.add_child(view)
    return collection


def _pending(ctx) -> int:
    return len(ctx._queries)


# --- update_all --------------------------------------------------------------


def test_update_all_is_deferred_and_queues_one_update_per_item():
    ctx, transport = _sp([])
    col = _loaded(ctx, "A", "B", "C")

    col.update_all(Title="Archived")

    assert transport.calls == 0
    assert _pending(ctx) == 3  # noqa: PLR2004
    assert col[0].properties["Title"] == "Archived"
    assert col[2].properties["Title"] == "Archived"


def test_update_all_executes_queued_updates():
    ctx, transport = _sp([{"d": {}}, {"d": {}}])
    col = _loaded(ctx, "A", "B")

    col.update_all(Status="Done").execute_query()

    assert transport.calls == 2  # noqa: PLR2004


# --- delete_all --------------------------------------------------------------


def test_delete_all_where_narrows_client_side():
    ctx, _ = _sp([])
    col = _loaded(ctx, "stale", "keep", "stale")

    col.delete_all(where=lambda i: i.properties["Title"] == "stale")

    assert _pending(ctx) == 2  # noqa: PLR2004
    assert [i.properties["Title"] for i in col] == ["keep"]


def test_delete_all_ignore_missing_is_idempotent():
    ctx, transport = _sp([_NOT_FOUND])
    col = _loaded(ctx, "A")

    col.delete_all(ignore_missing=True).execute_query()

    assert transport.calls == 1


def test_delete_all_raises_on_missing_by_default():
    ctx, _ = _sp([_NOT_FOUND])
    col = _loaded(ctx, "A")

    with pytest.raises(ObjectNotFoundException):
        col.delete_all().execute_query()


# --- List.clear delegates to delete_all --------------------------------------


def test_list_clear_loads_ids_then_queues_deletes():
    ctx, transport = _sp([{"d": {"results": [{"Id": 1}, {"Id": 2}]}}])
    lst = ctx.web.lists.get_by_title("Documents")

    lst.clear()

    assert transport.calls == 1  # only the ID load runs eagerly
    assert _pending(ctx) == 2  # noqa: PLR2004 — the deletes wait for execute_batch
