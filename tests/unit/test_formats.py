"""Unit tests for the data-pipeline formats and path|IO parity.

Covers tsv/json/ndjson (stdlib), parquet/orc/feather (pyarrow), and SQL/DuckDB
streaming — optional formats are skipped when their dependency is absent.
"""

from __future__ import annotations

import asyncio

import pytest
from office365.directory.users.user import User
from office365.graph_client import GraphClient
from office365.runtime.converters import registry
from office365.runtime.paths.resource_path import ResourcePath
from office365.runtime.record_collection import RecordCollection
from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.lists.list import List
from tests._scripted_transport import ScriptedTransport

RECORDS = [
    {"userPrincipalName": "a@contoso.com", "displayName": "A", "accountEnabled": True},
    {"userPrincipalName": "b@contoso.com", "displayName": "B", "accountEnabled": False},
]


def _collection(records):
    col = RecordCollection(GraphClient(), User, None)
    for props in records:
        col.add_child(col.create_typed_object(props))
    col.query_options.select = list(records[0].keys())
    return col


@pytest.mark.parametrize("fmt", ["parquet", "orc", "feather"])
def test_pyarrow_formats_round_trip(tmp_path, fmt):
    pytest.importorskip("pyarrow")
    path = tmp_path / f"data.{fmt}"

    registry.writer_for(fmt)(_collection(RECORDS), str(path))

    records = registry.reader_for(fmt)(str(path))
    assert [r["displayName"] for r in records] == ["A", "B"]


def test_streaming_csv_writer_appends_pages(tmp_path):
    from office365.runtime.converters.streamers import streamer_for

    path = tmp_path / "out.csv"
    stream = streamer_for("csv")(str(path))
    stream.write([{"a": 1, "b": "x"}])
    stream.write([{"a": 2, "b": "y"}])
    stream.close()

    assert path.read_text(encoding="utf-8").count("a,b") == 1  # header written once
    assert [r["a"] for r in registry.reader_for("csv")(str(path))] == ["1", "2"]


def test_streaming_json_writer_appends_pages(tmp_path):
    import json

    from office365.runtime.converters.streamers import streamer_for

    path = tmp_path / "out.json"
    stream = streamer_for("json")(str(path))
    stream.write([{"a": 1}])
    stream.write([{"a": 2}])
    stream.close()

    assert json.loads(path.read_text(encoding="utf-8")) == [{"a": 1}, {"a": 2}]


def test_duckdb_streaming_and_write():
    duckdb = pytest.importorskip("duckdb")
    from office365.runtime.converters.sql import duckdb_chunks, write_duckdb

    con = duckdb.connect()
    con.execute("CREATE TABLE src AS SELECT 'A' AS displayName, 1 AS n")

    assert list(duckdb_chunks(con, "SELECT * FROM src", 1)) == [[{"displayName": "A", "n": 1}]]

    write_duckdb(RECORDS, con, table="dst")
    assert con.execute("SELECT count(*) FROM dst").fetchone()[0] == len(RECORDS)  # noqa: PLR2004


# ── Async streaming export ───────────────────────────────────────

_GRAPH_NEXT = "https://graph.microsoft.com/v1.0/users?$skiptoken=abc"


def _sp_page(records):
    return {"d": {"results": records}}


def _list_context(payloads):
    ctx = ClientContext("https://contoso.sharepoint.com")
    ctx.pending_request().beforeExecute.clear()
    transport = ScriptedTransport(payloads)
    ctx.pending_request().transport = transport
    lst = List(ctx, ResourcePath("Web/Lists/getByTitle('Tasks')"))
    # `List.items` builds a fresh collection on each access; pin one instance.
    lst.properties["Items"] = lst.items
    return lst, transport


def test_export_to_streams_pages_sync(tmp_path):
    ctx = GraphClient()
    ctx.pending_request().beforeExecute.clear()
    transport = ScriptedTransport(
        [
            {"@odata.nextLink": _GRAPH_NEXT, "value": [{"displayName": "A"}, {"displayName": "B"}]},
            {"value": [{"displayName": "C"}]},
        ]
    )
    ctx.pending_request().transport = transport
    path = tmp_path / "users_sync.csv"

    ctx.users.export_to(str(path), format="csv", page_size=2).execute_query()

    assert transport.calls == 2  # noqa: PLR2004
    assert [r["displayName"] for r in registry.reader_for("csv")(str(path))] == ["A", "B", "C"]


def test_export_to_async_closes_stream_on_failure(tmp_path):
    from office365.runtime.client_request_exception import ClientRequestException

    ctx = GraphClient()
    ctx.pending_request().beforeExecute.clear()
    transport = ScriptedTransport([{"@odata.nextLink": _GRAPH_NEXT, "value": [{"id": "1"}]}, ("deny", None)])
    ctx.pending_request().transport = transport
    path = tmp_path / "partial.csv"

    with pytest.raises(ClientRequestException):
        asyncio.run(ctx.users.export_to_async(str(path), format="csv", page_size=1))

    # The first page was flushed and the writer closed despite the failure.
    assert [r["id"] for r in registry.reader_for("csv")(str(path))] == ["1"]


def test_list_export_to_async_streams_items(tmp_path):
    lst, transport = _list_context([_sp_page([{"Title": "A"}]), _sp_page([{"Title": "B"}]), _sp_page([])])
    path = tmp_path / "items.csv"

    asyncio.run(lst.export_to_async(str(path), page_size=1))

    assert transport.calls == 3  # noqa: PLR2004
    assert [r["Title"] for r in registry.reader_for("csv")(str(path))] == ["A", "B"]


def test_list_export_to_async_writes_loaded_items(tmp_path):
    lst, transport = _list_context([_sp_page([{"Title": "A"}, {"Title": "B"}])])
    path = tmp_path / "loaded.csv"

    asyncio.run(lst.export_to_async(str(path)))

    assert transport.calls == 1
    assert [r["Title"] for r in registry.reader_for("csv")(str(path))] == ["A", "B"]
