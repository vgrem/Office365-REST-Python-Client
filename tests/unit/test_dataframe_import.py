"""Tests for the generic, streaming, resumable ``ImportResult`` driver."""

from __future__ import annotations

import asyncio
import json
from typing import Any, cast

import pytest
from office365.migration.base import MigrationStats
from office365.runtime.client_object import ClientObject
from office365.runtime.converters.dataframe import dataframe_chunks
from office365.runtime.imports import ImportCheckpoint, ImportResult, ImportStats
from office365.runtime.operations import OperationStats
from office365.runtime.record_collection import RecordCollection

pd = pytest.importorskip("pandas")


class _FakeCollection:
    def __init__(self) -> None:
        self.queued: list[dict] = []
        self.clears = 0

    def queue_records(self, records, progress=None):
        self.queued.extend(records)
        return self

    def clear(self):
        self.clears += 1
        return self


class _FakeContext:
    def __init__(self) -> None:
        self.query_calls = 0
        self.batch_calls: list[dict] = []

    def execute_query(self):
        self.query_calls += 1
        return self

    def execute_batch(self, items_per_batch=100, max_batch_bytes=None, concurrency=1, success_callback=None):
        self.batch_calls.append({"items_per_batch": items_per_batch, "concurrency": concurrency})
        return self


class _FlakyContext(_FakeContext):
    def __init__(self, fail_on: int) -> None:
        super().__init__()
        self._fail_on = fail_on
        self.calls = 0

    def execute_query(self):
        self.calls += 1
        if self.calls == self._fail_on:
            raise RuntimeError("boom")
        return super().execute_query()


class _AsyncFakeContext(_FakeContext):
    """Async terminals mirroring ``_FakeContext`` (must be awaited)."""

    async def execute_query_async(self):
        self.query_calls += 1
        return self

    async def execute_batch_async(self, items_per_batch=100, max_batch_bytes=None, concurrency=1, success_callback=None):
        self.batch_calls.append({"items_per_batch": items_per_batch, "concurrency": concurrency})
        return self


class _AsyncFlakyContext(_AsyncFakeContext):
    def __init__(self, fail_on: int) -> None:
        super().__init__()
        self._fail_on = fail_on
        self.calls = 0

    async def execute_query_async(self):
        self.calls += 1
        if self.calls == self._fail_on:
            raise RuntimeError("boom")
        return await super().execute_query_async()


def _batches(*sizes: int) -> list[list[dict]]:
    out: list[list[dict]] = []
    n = 0
    for size in sizes:
        out.append([{"n": n + i} for i in range(size)])
        n += size
    return out


def _driver(context, collection, batches, **kwargs) -> ImportResult:
    return ImportResult(context, collection, batches, to_records=lambda b: b, **kwargs)


def test_execute_query_chunks_once_and_bounds_memory():
    ctx = _FakeContext()
    collection = _FakeCollection()
    driver = _driver(ctx, collection, _batches(2, 2, 1))

    driver.execute_query()

    assert collection.clears == 3  # noqa: PLR2004 — one clear per chunk
    assert driver.value.total == 5  # noqa: PLR2004
    assert driver.value.success == 5  # noqa: PLR2004
    assert driver.value.chunks == 3  # noqa: PLR2004
    assert ctx.query_calls == 3  # noqa: PLR2004
    assert len(collection.queued) == 5  # noqa: PLR2004


def test_dry_run_plans_without_queueing_or_executing():
    ctx = _FakeContext()
    collection = _FakeCollection()
    driver = _driver(ctx, collection, _batches(2, 2), dry_run=True)

    driver.execute_query()

    assert ctx.query_calls == 0  # nothing executed
    assert collection.queued == []  # nothing queued
    assert driver.value.total == 4  # noqa: PLR2004 — plan counted
    assert driver.value.success == 4  # noqa: PLR2004


def test_iter_yields_the_collection_and_drives_execution():
    ctx = _FakeContext()
    collection = _FakeCollection()
    driver = _driver(ctx, collection, _batches(1, 1, 1))

    for yielded in driver:
        assert yielded is collection
        ctx.execute_query()

    assert driver.value.total == 3  # noqa: PLR2004
    assert collection.clears == 3  # noqa: PLR2004


def test_checkpoint_round_trips(tmp_path):
    path = tmp_path / "ckpt.json"
    ImportCheckpoint(cursor=10, chunks=2, errors=1, failures=[{"records": 1, "error": "x"}]).save(path)

    loaded = ImportCheckpoint.load(path)

    assert loaded.cursor == 10  # noqa: PLR2004
    assert loaded.chunks == 2  # noqa: PLR2004
    assert loaded.errors == 1
    assert loaded.failures == [{"records": 1, "error": "x"}]


def test_resume_skips_committed_records(tmp_path):
    path = tmp_path / "ckpt.json"

    # first run commits the first two chunks (4 records)
    _driver(_FakeContext(), _FakeCollection(), _batches(2, 2), checkpoint=str(path)).execute_query()
    assert ImportCheckpoint.load(path).cursor == 4  # noqa: PLR2004

    # a resumed run (fresh source) skips the committed records
    collection = _FakeCollection()
    driver = _driver(_FakeContext(), collection, _batches(2, 2, 2), checkpoint=str(path))
    driver.execute_query()

    assert collection.queued == [{"n": 4}, {"n": 5}]
    assert driver.value.total == 2  # noqa: PLR2004
    assert driver.value.success == 2  # noqa: PLR2004


def test_resume_accessors_and_summary(tmp_path):
    path = tmp_path / "ckpt.json"
    _driver(_FakeContext(), _FakeCollection(), _batches(2, 2), checkpoint=str(path)).execute_query()

    driver = _driver(_FakeContext(), _FakeCollection(), _batches(2, 2, 2), checkpoint=str(path))
    assert driver.resumed_from == 4  # noqa: PLR2004
    assert driver.value.resumed_from == 4  # noqa: PLR2004
    assert driver.checkpoint.cursor == 4  # noqa: PLR2004

    driver.execute_query()

    assert driver.checkpoint.cursor == 6  # noqa: PLR2004
    assert "resumed at 4" in driver.value.summary()


def test_custom_checkpoint_store(tmp_path):
    from office365.runtime.imports import FileCheckpointStore, MemoryCheckpointStore

    store = MemoryCheckpointStore(ImportCheckpoint(cursor=2, chunks=1))
    driver = _driver(_FakeContext(), _FakeCollection(), _batches(2, 2), checkpoint=store)
    assert driver.resumed_from == 2  # noqa: PLR2004

    driver.execute_query()
    assert store.load().cursor == 4  # noqa: PLR2004

    file_store = FileCheckpointStore(tmp_path / "c.json")
    assert file_store.load().cursor == 0
    file_store.save(ImportCheckpoint(cursor=7))
    assert file_store.load().cursor == 7  # noqa: PLR2004


def test_on_error_collect_records_and_continues():
    ctx = _FlakyContext(fail_on=2)
    collection = _FakeCollection()
    checkpoint = ImportCheckpoint()
    driver = _driver(ctx, collection, _batches(2, 2, 2), checkpoint=checkpoint, on_error="collect")

    driver.execute_query()

    assert driver.value.total == 6  # noqa: PLR2004
    assert driver.value.success == 4  # noqa: PLR2004
    assert driver.value.errors == 2  # noqa: PLR2004
    assert len(checkpoint.failures) == 1
    assert checkpoint.failures[0]["records"] == 2  # noqa: PLR2004
    assert checkpoint.cursor == 6  # noqa: PLR2004 — failed chunk is skipped, not retried


def test_execute_batch_reports_progress_per_batch_and_forwards_callback():
    class _BatchingContext(_FakeContext):
        def execute_batch(self, items_per_batch=100, max_batch_bytes=None, concurrency=1, success_callback=None):
            for _ in range(2):  # two sub-batches of two items each
                if callable(success_callback):
                    success_callback([1, 2])
            return self

    seen: list[Any] = []
    forwarded: list[Any] = []
    driver = _driver(_BatchingContext(), _FakeCollection(), _batches(4), progress=seen.append, total=4)

    driver.execute_batch(items_per_batch=2, success_callback=forwarded.append)

    assert [p.done for p in seen] == [0, 2, 4]
    assert len(forwarded) == 2  # noqa: PLR2004


def test_dead_letter_isolates_the_failed_record(tmp_path):
    path = tmp_path / "dl.jsonl"
    ctx = _FlakyContext(fail_on=2)
    collection = _FakeCollection()
    driver = _driver(ctx, collection, _batches(2, 2, 2), on_error="collect", dead_letter=str(path))

    driver.execute_query()

    lines = path.read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) == 1  # only the failing row is dead-lettered
    entry = json.loads(lines[0])
    assert entry["row"] == 1
    assert entry["record"] == {"n": 1}
    assert entry["error"] == "boom"


def test_dataframe_chunks_reads_csv(tmp_path):
    path = tmp_path / "rows.csv"
    path.write_text("n\na\nb\nc\n", encoding="utf-8")
    chunks, total = dataframe_chunks(str(path), chunksize=1)

    assert total is None
    assert len(list(chunks)) == 3  # noqa: PLR2004


def test_list_from_dataframe_returns_import_result():
    from office365.sharepoint.lists.list import List

    ctx = _FakeContext()
    lst = List(cast(Any, ctx))
    driver = lst.from_dataframe(pd.DataFrame({"Name": ["a"], "Value": [1]}))

    assert isinstance(driver, ImportResult)


def test_import_and_migration_stats_share_the_operation_base():
    assert issubclass(ImportStats, OperationStats)
    assert issubclass(MigrationStats, OperationStats)

    # a common-stats consumer accepts either specialization without conversion
    def totals(stats: OperationStats) -> tuple[int, int, int]:
        return stats.total, stats.success, stats.errors

    assert totals(ImportStats(total=10, success=8, errors=2)) == (10, 8, 2)  # noqa: PLR2004
    assert totals(MigrationStats(total=5, success=4, errors=1)) == (5, 4, 1)  # noqa: PLR2004


def test_collection_clear_discards_items():
    from office365.runtime.client_object import ClientObject
    from office365.runtime.client_object_collection import ClientObjectCollection

    ctx = _FakeContext()
    collection = ClientObjectCollection(cast(Any, ctx), ClientObject)
    collection.add_child(ClientObject(cast(Any, ctx)))

    collection.clear()

    assert len(collection) == 0


class _KeyedTarget:
    def __init__(self, keys: list[str]) -> None:
        self._keys = keys

    def load_keys(self):
        return {key: index for index, key in enumerate(self._keys)}


class _KeyedCollection(_FakeCollection):
    def __init__(self, keys: list[str]) -> None:
        super().__init__()
        self._keys = keys

    def upsert_target(self, *, key_field: str = "MigrationKey", enforce_unique: bool = False):
        return _KeyedTarget(self._keys)


def test_from_records_applies_column_mapping():
    from office365.runtime.client_object import ClientObject
    from office365.runtime.record_collection import RecordCollection

    class _RecordFake(RecordCollection):
        def __init__(self, context):
            super().__init__(context, ClientObject)
            self.queued = []

        def queue_records(self, records, progress=None):
            self.queued.extend(records)
            return self

    collection = _RecordFake(cast(Any, _FakeContext()))
    result = RecordCollection.from_records(
        collection,
        _batches(1),
        format="records",
        to_records=lambda b: b,
        mapping={"n": "value"},
    )

    result.execute_query()

    assert collection.queued == [{"value": 0}]


def test_verify_keys_reports_missing():
    from office365.runtime.record_collection import RecordCollection, VerificationResult

    result = RecordCollection.verify_keys(cast(Any, _KeyedCollection(["a", "b"])), ["a", "b", "c"])

    assert isinstance(result, VerificationResult)
    assert result.checked == 3  # noqa: PLR2004
    assert result.source_count == 3  # noqa: PLR2004
    assert result.target_count == 2  # noqa: PLR2004
    assert result.missing == ["c"]
    assert not result.ok
    assert "MISMATCH" in result.summary()


def test_import_result_run_is_the_batch_terminal():
    ctx = _FakeContext()
    driver = _driver(ctx, _FakeCollection(), _batches(2, 2))

    driver.run(items_per_batch=2, concurrency=3)

    assert len(ctx.batch_calls) == 2  # noqa: PLR2004 — one batch call per chunk
    assert all(call == {"items_per_batch": 2, "concurrency": 3} for call in ctx.batch_calls)


def test_collection_verify_reconciles_source_keys():
    from office365.runtime.converters.upsert import record_key
    from office365.runtime.record_collection import RecordCollection

    existing = {record_key({"id": 1}, ["id"]): 11}
    collection = _ImportCollection(existing=existing)

    report = RecordCollection.verify(collection, [[{"id": 1}, {"id": 2}]], key=["id"], format="records")

    assert report.source_count == 2  # noqa: PLR2004
    assert report.target_count == 1
    assert report.missing == [record_key({"id": 2}, ["id"])]
    assert not report.ok


def test_import_result_verify_delegates_to_collection():
    from office365.runtime.converters.upsert import record_key
    from office365.runtime.imports import ImportResult

    existing = {record_key({"id": 1}, ["id"]): 11}
    collection = _ImportCollection(existing=existing)
    driver = ImportResult(
        cast(Any, collection.context),
        collection,
        [[{"id": 1}, {"id": 2}]],
        to_records=lambda batch: batch,
    )

    report = driver.verify([[{"id": 1}, {"id": 2}]], key=["id"], format="records")

    assert report.missing == [record_key({"id": 2}, ["id"])]


class _ImportTarget:
    """Fake keyed target recording the key-load/ensure calls."""

    def __init__(self, collection: "_ImportCollection", key_field: str) -> None:
        self._collection = collection
        self._key_field = key_field

    @property
    def key_field(self) -> str:
        return self._key_field

    def ensure_key_field(self) -> None:
        self._collection.ensured += 1

    def load_keys(self):
        self._collection.load_calls += 1
        return dict(self._collection.existing)

    def create_records(self, records: list[dict]) -> None:
        self._collection.created.extend(records)

    def update_record(self, item_id, record: dict) -> None:
        self._collection.updated.append((item_id, record))


class _ImportCollection(RecordCollection):
    """Fake record collection driving the real ``RecordCollection.from_records``."""

    def __init__(self, existing: dict | None = None) -> None:
        super().__init__(cast(Any, _FakeContext()), ClientObject)
        self.existing = dict(existing or {})
        self.created: list[dict] = []
        self.updated: list = []
        self.load_calls = 0
        self.ensured = 0

    def queue_records(self, records, progress=None):
        self.created.extend(records)
        return self

    def upsert_target(self, *, key_field: str = "MigrationKey", enforce_unique: bool = False):
        return _ImportTarget(self, key_field)


def test_resume_loads_existing_keys_and_skips_duplicates():
    from office365.runtime.converters.upsert import record_key
    from office365.runtime.imports import ImportCheckpoint
    from office365.runtime.record_collection import RecordCollection

    existing = {record_key({"id": 1}, ["id"]): 11}
    collection = _ImportCollection(existing=existing)
    checkpoint = ImportCheckpoint(cursor=1, chunks=1)  # skip the first batch

    driver = RecordCollection.from_records(
        collection,
        [[{"id": 0}], [{"id": 1}], [{"id": 2}]],
        format="records",
        key=["id"],
        checkpoint=checkpoint,
    )
    driver.execute_query()

    assert collection.load_calls == 1  # keys are loaded on a resumed run too
    assert collection.ensured == 1
    assert [record["id"] for record in collection.created] == [2]  # id=1 skipped by key
    assert collection.created[0]["MigrationKey"] == record_key({"id": 2}, ["id"])


def test_checkpoint_signature_mismatch_rescans_from_start():
    from office365.runtime.imports import ImportCheckpoint
    from office365.runtime.record_collection import RecordCollection

    checkpoint = ImportCheckpoint(cursor=1, chunks=1, signature={"format": "records", "chunk_size": 2000})
    collection = _ImportCollection()

    with pytest.warns(UserWarning, match="signature changed"):
        driver = RecordCollection.from_records(
            collection,
            [[{"id": 0}], [{"id": 1}]],
            format="records",
            chunksize=1000,  # differs from the stored signature
            key=["id"],
            checkpoint=checkpoint,
        )

    assert driver.resumed_from == 0  # chunk skip discarded
    driver.execute_query()
    assert [record["id"] for record in collection.created] == [0, 1]  # re-scanned


def test_from_records_applies_coerce_converters():
    from office365.runtime.record_collection import RecordCollection

    collection = _ImportCollection()
    driver = RecordCollection.from_records(
        collection,
        [[{"n": 2}]],
        format="records",
        coerce={"n": lambda value: value * 2},
    )
    driver.execute_query()

    assert collection.created == [{"n": 4}]


# --------------------------------------------------------------------------
# Async terminals (B6): execute_query_async / execute_batch_async / run_async
# --------------------------------------------------------------------------


def test_import_result_run_async_is_the_batch_terminal():
    ctx = _AsyncFakeContext()
    driver = _driver(ctx, _FakeCollection(), _batches(2, 2))

    asyncio.run(driver.run_async(items_per_batch=2, concurrency=3))

    assert len(ctx.batch_calls) == 2  # noqa: PLR2004 — one batch call per chunk
    assert all(call == {"items_per_batch": 2, "concurrency": 3} for call in ctx.batch_calls)


def test_on_error_raise_async_aborts():
    ctx = _AsyncFlakyContext(fail_on=2)
    collection = _FakeCollection()
    driver = _driver(ctx, collection, _batches(2, 2, 2))

    with pytest.raises(RuntimeError):
        asyncio.run(driver.execute_query_async())

    assert driver.value.success == 2  # noqa: PLR2004
    assert driver.value.errors == 2  # noqa: PLR2004


def test_aiter_yields_the_collection_and_drives_execution():
    ctx = _AsyncFakeContext()
    collection = _FakeCollection()
    driver = _driver(ctx, collection, _batches(1, 1, 1))

    async def _consume():
        async for yielded in driver:
            assert yielded is collection
            await ctx.execute_query_async()

    asyncio.run(_consume())

    assert driver.value.total == 3  # noqa: PLR2004
    assert collection.clears == 3  # noqa: PLR2004
    assert ctx.query_calls == 3  # noqa: PLR2004


def test_execute_query_async_uses_the_native_async_terminal():
    """A real context + async-only transport proves no worker thread is used."""
    from office365.runtime.queries.read_entity import ReadEntityQuery
    from office365.sharepoint.client_context import ClientContext
    from tests._scripted_transport import AsyncScriptedTransport

    ctx = ClientContext("https://contoso.sharepoint.com/sites/dev")
    ctx.pending_request().beforeExecute.clear()
    transport = AsyncScriptedTransport([{"d": {"Title": "ok"}}] * 3)
    ctx.pending_request().transport = transport
    collection = _FakeCollection()

    def queue(records):
        ctx.add_query(ReadEntityQuery(ctx.web))  # one real request per chunk
        return len(records), 0

    driver = _driver(ctx, collection, _batches(1, 1, 1), queue=queue)

    asyncio.run(driver.execute_query_async())

    assert transport.calls == 3  # noqa: PLR2004
    assert driver.value.success == 3  # noqa: PLR2004
