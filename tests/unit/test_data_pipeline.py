"""Merged unit tests (consolidated; see git history for originals)."""

from __future__ import annotations

import io
import unittest
import warnings
from datetime import datetime, timezone
from typing import cast

import pytest
from office365.directory.users.user import User
from office365.graph_client import GraphClient
from office365.runtime.client_runtime_context import ClientRuntimeContext
from office365.runtime.converters.csv_reader import coerce_records, read_csv_records
from office365.runtime.converters.csv_writer import write_csv
from office365.runtime.converters.dataframe import (
    DataFrameResult,
    series_kind,
    write_dataframe,
)
from office365.runtime.converters.excel import read_excel, write_excel
from office365.runtime.operations import query_progress_hook
from office365.runtime.queries.client_query import ClientQuery
from office365.runtime.record_collection import RecordCollection
from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.fields.collection import field_type_from_kind
from office365.sharepoint.fields.type import FieldType
from office365.sharepoint.listitems.collection import ListItemCollection
from tests import test_site_url

CSV_TEXT = (
    "userPrincipalName,givenName,displayName,accountEnabled,officeLocation,"
    "passwordProfile/password,passwordProfile/forceChangePasswordNextSignIn,businessPhones\n"
    "jdoe@contoso.com,John,John Doe,True,Seattle,S3cret!,True,+1-555-0101; +1-555-0102\n"
)


def _graph_client() -> GraphClient:
    """An unauthenticated client: these tests only queue records, never send them."""
    return GraphClient()


class TestCsvRecords(unittest.TestCase):
    def test_coerce_records(self):
        records = coerce_records(
            User,
            read_csv_records(io.StringIO(CSV_TEXT)),
        )
        self.assertEqual(len(records), 1)
        record = records[0]
        self.assertEqual(record["userPrincipalName"], "jdoe@contoso.com")
        self.assertEqual(record["passwordProfile"], {"password": "S3cret!", "forceChangePasswordNextSignIn": "True"})
        self.assertEqual(record["businessPhones"], ["+1-555-0101", "+1-555-0102"])

    def test_coerce_records_strips_non_importable_and_unknown(self):
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            records = coerce_records(
                User,
                [
                    {
                        "userPrincipalName": "jdoe@contoso.com",
                        "id": "42",
                        "@odata.type": "user",
                        "noSuchColumn": "x",
                    }
                ],
            )
        self.assertEqual(records, [{"userPrincipalName": "jdoe@contoso.com"}])
        self.assertTrue(any("noSuchColumn" in str(w.message) for w in caught))


class TestImportPipeline(unittest.TestCase):
    def test_from_csv_queues_creates(self):
        client = _graph_client()
        users = next(iter(client.users.from_csv(io.StringIO(CSV_TEXT))))
        self.assertEqual(len(users), 1)
        self.assertEqual(len(client._queries), 1)
        user = users[0]
        self.assertIs(user.get_property("accountEnabled"), True)
        self.assertEqual(user.get_property("passwordProfile").password, "S3cret!")
        self.assertIs(user.get_property("passwordProfile").forceChangePasswordNextSignIn, True)
        self.assertEqual(list(user.get_property("businessPhones")), ["+1-555-0101", "+1-555-0102"])

    def test_round_trip_write_then_read(self):
        col = RecordCollection(cast(ClientRuntimeContext, None), User, None)
        item = col.create_typed_object(
            {
                "userPrincipalName": "jdoe@contoso.com",
                "displayName": "John Doe",
                "accountEnabled": True,
                "createdDateTime": datetime(2025, 1, 15, 12, 34, 56, tzinfo=timezone.utc),
                "businessPhones": ["+1-555-0101", "+1-555-0102"],
            }
        )
        col.add_child(item)
        col.query_options.select = [
            "userPrincipalName",
            "displayName",
            "accountEnabled",
            "createdDateTime",
            "businessPhones",
        ]
        out = io.StringIO()
        write_csv(col, out)

        client = _graph_client()
        users = next(iter(client.users.from_csv(io.StringIO(out.getvalue()))))
        user = users[0]
        self.assertIs(user.get_property("accountEnabled"), True)
        self.assertEqual(user.get_property("createdDateTime"), datetime(2025, 1, 15, 12, 34, 56, tzinfo=timezone.utc))
        self.assertEqual(list(user.get_property("businessPhones")), ["+1-555-0101", "+1-555-0102"])


def test_list_item_collection_from_records_keeps_custom_columns():
    ctx = ClientContext(test_site_url)
    col = ListItemCollection(ctx)
    col.queue_records([{"Title": "row", "CustomColumn": 42}])

    assert len(col) == 1
    assert col[0].get_property("CustomColumn") == 42  # noqa: PLR2004
    assert col[0].get_property("Title") == "row"


# ruff: noqa: E402  (imports must follow the importorskip guard)


openpyxl = pytest.importorskip("openpyxl")


def pipeline__collection(properties: list[dict], context=None) -> RecordCollection:
    col = RecordCollection(context or cast(ClientRuntimeContext, None), User, None)
    for props in properties:
        col.add_child(col.create_typed_object(props))
    return col


def test_excel_round_trip(tmp_path):
    records = [{"Name": "John", "Age": 30}, {"Name": "Alice", "Age": 25}]
    path = str(tmp_path / "out.xlsx")
    write_excel(records, path)
    assert read_excel(path) == records


def test_query_progress_hook():
    events = []
    hook = query_progress_hook(3, events.append, stage="importing")
    for _ in range(3):
        hook(None)  # each call mimics one queued query completing
    assert [p.done for p in events] == [1, 2, 3]  # noqa: PLR2004
    assert all(p.total == 3 for p in events)  # noqa: PLR2004
    assert all(p.stage == "importing" for p in events)
    assert events[-1].percent == 100.0  # noqa: PLR2004


def test_deferred_operation_query():
    from office365.runtime.queries.deferred import DeferredOperationQuery

    client = GraphClient()
    barrier = DeferredOperationQuery(client)
    client.add_query(barrier)

    add = ClientQuery(client)
    barrier.defer(add)  # swaps the placeholder's slot for the real query
    assert list(client._queries) == [add]

    client2 = GraphClient()
    barrier2 = DeferredOperationQuery(client2)
    client2.add_query(barrier2)
    barrier2.resolve()  # no operation needed — drops the placeholder
    assert list(client2._queries) == []


def test_ensure_property_cached_queues_deferred_noop():
    user = GraphClient().users["123"]
    user.set_property("id", "123")
    user.set_property("displayName", "John Doe")
    user.ensure_property("displayName")  # already loaded — no redundant GET
    from office365.runtime.queries.deferred import DeferredOperationQuery

    assert isinstance(user.context._queries[-1], DeferredOperationQuery)


def test_get_all_accepts_progress():
    client = GraphClient()
    col = RecordCollection(client, User, None)
    events = []
    col.get_all(progress=events.append)
    assert len(client._queries) >= 1  # the first page query is queued


# ruff: noqa: E402  (imports must follow the importorskip guard)


pd = pytest.importorskip("pandas")


def test_flat_round_trip():
    client = GraphClient()
    col = pipeline__collection(
        [
            {"userPrincipalName": "jdoe@contoso.com", "displayName": "John Doe", "accountEnabled": True},
        ],
        context=client,
    )
    col.query_options.select = ["userPrincipalName", "displayName", "accountEnabled"]

    target = DataFrameResult(client)
    write_dataframe(col, target)

    imported = RecordCollection(client, User, None)
    imported.queue_dataframe(target.value)
    assert len(imported) == 1
    item = imported[0]
    assert item.get_property("userPrincipalName") == "jdoe@contoso.com"
    assert item.get_property("accountEnabled") is True


def test_to_dataframe_returns_dataframe_result():
    client = GraphClient()
    col = pipeline__collection([{"displayName": "John Doe"}], context=client)
    result = col.to_dataframe()
    assert isinstance(result, DataFrameResult)
    # the after_execute callback materializes .value on the loaded collection
    write_dataframe(col, result)
    assert list(result.value.columns) == ["displayName"]


def test_field_type_mapping():
    assert field_type_from_kind(series_kind(pd, pd.Series([True]))) is FieldType.Boolean
    assert field_type_from_kind(series_kind(pd, pd.Series(pd.to_datetime(["2025-01-01"])))) is FieldType.DateTime
    assert field_type_from_kind(series_kind(pd, pd.Series([1.5]))) is FieldType.Number
    assert field_type_from_kind(series_kind(pd, pd.Series(["text"]))) is FieldType.Text


def test_internal_field_name_sanitizes_and_avoids_reserved_titles():
    from office365.sharepoint.fields.name import internal_field_name, is_reserved_field_title

    assert internal_field_name("My Column") == "My_Column"
    assert internal_field_name("Symbol") == "Symbol"
    # reserved built-in display names are suffixed so the column can be created
    assert internal_field_name("Name") == "Name_"
    assert internal_field_name("Title") == "Title_"
    assert is_reserved_field_title("name")
    assert not is_reserved_field_title("Symbol")
