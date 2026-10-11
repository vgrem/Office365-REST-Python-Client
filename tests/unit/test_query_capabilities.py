"""Offline tests for declarative OData query-option capabilities.

Covers the ``@query_capabilities`` declaration, its collection into the model,
and the guard the ``ClientObjectCollection`` fluent setters apply — including the
``callRecords`` feed, which rejects ``$top``.
"""

from __future__ import annotations

import pytest
from office365.communications.callrecords.collection import CallRecordCollection
from office365.entity import Entity
from office365.entity_collection import EntityCollection
from office365.graph_client import GraphClient
from office365.onedrive.driveitems.collection import DriveItemCollection
from office365.runtime.http.prefer import TRY_FILTER_LAST_MODIFIED_DATE_TIME
from office365.runtime.query_capabilities import (
    QueryOptionNotSupportedError,
    QueryPropertyNotSupportedError,
    query_capabilities,
    query_capabilities_of,
    referenced_properties,
)
from tests._scripted_transport import ScriptedTransport


def test_call_records_declares_top_unsupported():
    capability = query_capabilities_of(CallRecordCollection)
    assert capability is not None
    assert capability.supports("filter")
    assert not capability.supports("top")
    assert not capability.supports("$Top")  # normalized


def test_call_records_top_raises():
    records = GraphClient().communications.call_records
    with pytest.raises(QueryOptionNotSupportedError) as err:
        records.top(20)
    assert "$top" in str(err.value)


def test_paged_and_get_all_are_guarded():
    records = GraphClient().communications.call_records
    with pytest.raises(QueryOptionNotSupportedError):
        records.paged(20)
    with pytest.raises(QueryOptionNotSupportedError):
        records.get_all(page_size=20)


@query_capabilities(allowed={"filter", "select"})
class _FilterSelectOnly(EntityCollection):
    pass


def test_allow_list_guards_other_options():
    col = _FilterSelectOnly(GraphClient(), Entity)
    col.filter("id eq '1'")
    col.select(["id"])
    with pytest.raises(QueryOptionNotSupportedError):
        col.top(1)
    with pytest.raises(QueryOptionNotSupportedError):
        col.order_by("id")


@query_capabilities(unsupported={"top"}, on_unsupported="warn")
class _WarnTop(EntityCollection):
    pass


def test_warn_mode_skips_the_option():
    col = _WarnTop(GraphClient(), Entity)
    with pytest.warns(UserWarning):
        col.top(5)
    assert col.query_options.top is None


def test_declaration_validation():
    with pytest.raises(ValueError):
        query_capabilities(unsupported={"top"}, allowed={"filter"})
    with pytest.raises(ValueError):
        query_capabilities(unsupported={"top"}, on_unsupported="nope")


def test_decorator_rejects_non_class():
    with pytest.raises(TypeError):
        query_capabilities(unsupported={"top"})(lambda: None)


# --- property-level capabilities -------------------------------------------------


@pytest.mark.parametrize(
    ("expression", "expected"),
    [
        ("size gt 0", {"size"}),
        ("name eq 'size'", {"name"}),  # the quoted literal is not a property
        ("startswith(name,'A')", {"name"}),  # a function name is not a property
        ("folder ne null and size gt 0", {"folder", "size"}),
        ("lastModifiedDateTime gt 2020-01-01T00:00:00Z", {"lastModifiedDateTime"}),
        ("fields/customField eq 1", {"fields", "customField"}),
        (None, set()),
    ],
)
def test_referenced_properties(expression, expected):
    assert referenced_properties(expression) == expected


@query_capabilities(unsupported_filter={"size"}, unsupported_orderby={"name"})
class _PropertyRestricted(EntityCollection):
    pass


@query_capabilities(filterable={"name"}, orderable={"name"})
class _PropertyAllowList(EntityCollection):
    pass


def test_property_deny_list_violations():
    capability = query_capabilities_of(_PropertyRestricted)
    assert capability is not None
    assert capability.filter_violations("size gt 0") == ("size",)
    assert capability.filter_violations("folder ne null") == ()
    assert capability.orderby_violations("name desc") == ("name",)


def test_property_allow_list_violations():
    capability = query_capabilities_of(_PropertyAllowList)
    assert capability is not None
    assert capability.filter_violations("name eq 'a'") == ()
    assert capability.filter_violations("size gt 0") == ("size",)


def test_property_violation_raises_before_the_round_trip():
    col = _PropertyRestricted(GraphClient(), Entity)
    with pytest.raises(QueryPropertyNotSupportedError) as err:
        col.filter("size gt 0")
    assert "size" in str(err.value)
    assert "$filter" in str(err.value)


def test_property_violation_warn_keeps_the_expression():
    @query_capabilities(unsupported_filter={"size"}, on_unsupported="warn")
    class _WarnProperty(EntityCollection):
        pass

    col = _WarnProperty(GraphClient(), Entity)
    with pytest.warns(UserWarning):
        col.filter("size gt 0")
    assert col.query_options.filter == "size gt 0"


def test_drive_item_capability():
    capability = query_capabilities_of(DriveItemCollection)
    assert capability is not None
    assert capability.filter_violations("size gt 0") == ("size",)
    assert capability.filter_violations("folder ne null") == ()
    assert capability.orderby_violations("size desc") == ()  # sorting by size is fine
    col = DriveItemCollection(GraphClient())
    with pytest.raises(QueryPropertyNotSupportedError):
        col.filter("size gt 0")
    col.order_by("size desc")  # allowed


class _RecordingTransport(ScriptedTransport):
    """Scripted transport that also records the requests it received."""

    def __init__(self, payloads):
        super().__init__(payloads)
        self.requests = []

    def execute(self, request):
        self.requests.append(request)
        return super().execute(request)


def _client(transport) -> GraphClient:
    client = GraphClient()
    client.pending_request().beforeExecute.clear()
    client.pending_request().transport = transport
    return client


def test_prefer_header_injected_for_last_modified_filter():
    transport = _RecordingTransport([{"value": []}])
    client = _client(transport)

    client.me.drive.root.children.filter("lastModifiedDateTime gt 2020-01-01T00:00:00Z").get().execute_query()

    prefer = transport.requests[-1].headers.get("Prefer", "")
    assert TRY_FILTER_LAST_MODIFIED_DATE_TIME in prefer


def test_prefer_header_absent_without_matching_filter():
    transport = _RecordingTransport([{"value": []}])
    client = _client(transport)

    client.me.drive.root.children.filter("folder ne null").get().execute_query()

    assert "Prefer" not in (transport.requests[-1].headers or {})
