"""A collection that can be exported to / imported from tabular and record formats.

Keeps the data-interchange concern (pandas/CSV/JSON/NDJSON/Excel) out of the core
:class:`~office365.runtime.client_object_collection.ClientObjectCollection`, and
exposes named conveniences (``to_csv``/``from_dataframe``/``queue_dataframe`` …)
and unified ``export_to``/``from_records`` entry points backed by a format
registry. ``from_*`` is the **streaming** entry (returns an
:class:`~office365.runtime.imports.ImportResult` driver — bounded, resumable,
idempotent); ``queue_*`` is the deferred queue-all entry.

Keyed imports (skip/upsert) are opt-in: a subclass exposes an
:class:`~office365.runtime.converters.upsert.UpsertTarget` via :meth:`upsert_target`.
The single-entity counterpart, :meth:`RecordCollection.upsert`, reconciles one
entity by key (create-if-missing, else write-idempotent update).
"""

from __future__ import annotations

from os import PathLike
from typing import IO, TYPE_CHECKING, Any, Callable, Dict, Iterable, List, Optional, Protocol, Union, cast

from typing_extensions import Self

from office365.runtime.client_object import ClientObjectT
from office365.runtime.client_object_collection import ClientObjectCollection
from office365.runtime.converters import registry
from office365.runtime.limits import SAFE_PAGE_SIZE
from office365.runtime.verification import VerificationReport

if TYPE_CHECKING:
    from office365.runtime.converters.dataframe import DataFrameResult
    from office365.runtime.converters.upsert import UpsertTarget
    from office365.runtime.imports import CheckpointStore, ImportCheckpoint, ImportResult
    from office365.runtime.operations import ProgressCallback


# The pipeline and the migration toolkit share one reconciliation report type.
VerificationResult = VerificationReport


class _UpdatableEntity(Protocol):
    """Minimal view of an entity whose changed properties can be written back.

    Both the Graph and SharePoint ``Entity`` expose ``update()``; neither shares
    a runtime base, so the upsert verb reconciles through this structural type.
    """

    def update(self) -> Any:
        """Queue an update of the changed properties."""
        ...


def _apply_mapping(convert: Callable[[Any], list[dict]], mapping: Dict[str, str]) -> Callable[[Any], list[dict]]:
    """Wrap a chunk converter to rename record keys (``source -> target``)."""

    def mapped(chunk: Any) -> list[dict]:
        return [{mapping.get(k, k): v for k, v in record.items()} for record in convert(chunk)]

    return mapped


class RecordCollection(ClientObjectCollection[ClientObjectT]):
    """A collection with record import/export capabilities."""

    # ── Export ───────────────────────────────────────────────────

    def export_to(self, target: Any, *, format: str = "csv", page_size: Optional[int] = None, **opts: Any) -> Self:  # noqa: A002
        """Deferred export of the loaded items to ``target`` in ``format``.

        The writer is resolved from the format registry, so formats are pluggable.
        Pass ``page_size`` to **stream** an appendable format (CSV/TSV/NDJSON/JSON)
        page by page — bounded memory for large collections:

            >>> client.users.get_all().export_to(f, format="csv").execute_query()
            >>> lst.items.export_to("out.csv", page_size=2000).execute_query()
        """
        if page_size:
            return self._export_paged(target, format, page_size, opts)
        writer = registry.writer_for(format)
        return self.after_execute(lambda _: writer(self, target, **opts))

    def _export_paged(self, target: Any, format: str, page_size: int, opts: Dict[str, Any]) -> Self:  # noqa: A002
        """Page through the collection and append records (bounded memory)."""
        from office365.runtime.converters import streamers
        from office365.runtime.converters.records import records_from_items

        factory = streamers.streamer_for(format)
        if factory is None:  # not appendable — write the whole collection at once
            writer = registry.writer_for(format)
            return self.after_execute(lambda _: writer(self, target, **opts))

        stream = factory(target, **opts)
        state = {"start": 0}

        def _on_page(col: ClientObjectCollection) -> None:
            # Read ``_data`` directly: ``list(col)`` would run the synchronous
            # ``__iter__`` paging generator and pull every page inside this
            # callback, defeating the bounded-memory streaming.
            items = col._data[state["start"] :]
            state["start"] = len(col._data)
            stream.write(records_from_items(items, col.query_options.select, col.query_options.expand))
            if not col.has_next:
                stream.close()

        self.get_all(page_size=page_size, page_loaded=_on_page)
        return self

    async def export_to_async(
        self,
        target: Any,
        *,
        format: str = "csv",  # noqa: A002
        page_size: Optional[int] = None,
        **opts: Any,
    ) -> Self:
        """Async twin of :meth:`export_to`.

        Pass ``page_size`` to stream an appendable format (CSV/TSV/NDJSON/JSON)
        page by page: each page is fetched through the server-driven paging and
        projected/written on the worker pool, so a multi-million-row export stays
        memory-bounded and never blocks the event loop. Without ``page_size`` the
        already-loaded items are written in a single pass (also off the loop).

            >>> await client.users.export_to_async("users.csv", page_size=2000)
            >>> await lst.items.export_to_async("out.ndjson", format="ndjson", page_size=2000)
        """
        if page_size:
            return await self._export_paged_async(target, format, page_size, opts)

        from office365.runtime.transport.offload import run_offloaded

        writer = registry.writer_for(format)
        await run_offloaded(writer, self, target, **opts)
        return self

    async def _export_paged_async(self, target: Any, format: str, page_size: int, opts: Dict[str, Any]) -> Self:  # noqa: A002
        """Page through the collection and append records without blocking the loop."""
        from office365.runtime.converters import streamers
        from office365.runtime.converters.records import records_from_items
        from office365.runtime.transport.offload import get_offload_executor, run_offloaded

        executor = get_offload_executor()
        factory = streamers.streamer_for(format)
        if factory is None:  # not appendable — write the whole collection at once
            writer = registry.writer_for(format)
            await run_offloaded(writer, self, target, executor=executor, **opts)
            return self

        stream = await run_offloaded(factory, target, executor=executor, **opts)
        start = 0
        closed = False

        def _project(items: List[Any]) -> None:
            stream.write(records_from_items(items, self.query_options.select, self.query_options.expand))

        async def _append_page() -> None:
            nonlocal start
            # Read ``_data`` directly: ``list(self)`` would run the synchronous
            # ``__iter__`` paging generator and block the loop.
            items = self._data[start:]
            start = len(self._data)
            await run_offloaded(_project, items, executor=executor)

        async def _close() -> None:
            nonlocal closed
            if not closed:
                closed = True
                await run_offloaded(stream.close, executor=executor)

        try:
            self.paged(page_size)
            self.get()
            await self.context.execute_query_async()
            await _append_page()
            while self.has_next:
                self._get_next()
                await self.context.execute_query_async()
                await _append_page()
        finally:
            await _close()
        return self

    def to_records(self, raw: bool = False) -> List[Dict[str, Any]]:
        """Project loaded items into plain dict records — the neutral export form.

        The projection shared by every exporter: ``.select()``/``.expand()``
        columns, one record per expanded child item, native JSON-safe values.
        Unlike ``to_csv`` this returns a value directly, so load first.

        Args:
            raw: When True, keep native property values (no JSON coercion).
        """
        from office365.runtime.converters.records import iter_records

        return iter_records(self, raw=raw)

    def to_csv(self, file: IO[str]) -> Self:
        """Export loaded items to CSV (deferred)."""
        return self.export_to(file, format="csv")

    def to_ndjson(self, file: IO[str]) -> Self:
        """Export loaded items as NDJSON — one record per line (deferred)."""
        return self.export_to(file, format="ndjson")

    def to_excel(self, target: Union[str, PathLike]) -> Self:
        """Export loaded items to an Excel (.xlsx) worksheet (deferred).

        Requires the optional dependency (``pip install
        office365-rest-python-client[excel]``).
        """
        return self.export_to(target, format="excel")

    def to_parquet(self, target: Any) -> Self:
        """Export loaded items to Parquet (deferred; requires the ``[parquet]`` extra)."""
        return self.export_to(target, format="parquet")

    def to_orc(self, target: Any) -> Self:
        """Export loaded items to ORC (deferred; requires the ``[parquet]`` extra)."""
        return self.export_to(target, format="orc")

    def to_feather(self, target: Any) -> Self:
        """Export loaded items to Feather (deferred; requires the ``[parquet]`` extra)."""
        return self.export_to(target, format="feather")

    def to_sql(self, target: Any, *, table: str, **opts: Any) -> Self:
        """Write loaded items to a SQL table (deferred; requires the ``[sql]`` extra)."""
        from office365.runtime.converters.records import iter_records
        from office365.runtime.converters.sql import write_sql

        return self.after_execute(lambda _: write_sql(iter_records(self), target, table=table, **opts))

    def to_duckdb(self, target: Any, *, table: str, **opts: Any) -> Self:
        """Write loaded items to a DuckDB table (deferred; requires the ``[duckdb]`` extra)."""
        from office365.runtime.converters.records import iter_records
        from office365.runtime.converters.sql import write_duckdb

        return self.after_execute(lambda _: write_duckdb(iter_records(self), target, table=table, **opts))

    def to_dataframe(self) -> "DataFrameResult":
        """Build a pandas DataFrame from the loaded items (deferred result).

        Returns a ``DataFrameResult`` whose ``.value`` holds the DataFrame after
        ``execute_query()``. Requires the ``[pandas]`` extra.
        """
        from office365.runtime.converters.dataframe import DataFrameResult, require_pandas, write_dataframe

        require_pandas()  # fail fast on a missing optional dependency
        result = DataFrameResult(self.context)
        self.after_execute(lambda _: write_dataframe(self, result))
        return result

    # ── Single-entity idempotent write ───────────────────────────

    def upsert(
        self,
        key: str,
        value: Union[int, str],
        /,
        *,
        on_conflict: str = "update",
        **properties: Any,
    ) -> ClientObjectT:
        """Create the entity matching ``key == value`` or reconcile it (idempotent).

        The library's single-entity counterpart of the bulk keyed import: it looks
        the entity up by ``key`` and then either **creates** it (missing) or
        **updates** it (present), so a re-run converges on one resource. Nothing is
        sent until the caller runs ``execute_query()``:

            group = client.groups.upsert(
                "uniqueName", "Group157", displayName="Group157", description="Team site"
            ).execute_query()

        The lookup uses ``$filter`` (``key eq value``), so ``key`` must be a
        filterable property that identifies the entity — a primary key (``id``),
        an alternate key (``uniqueName``, ``appId``, ``userPrincipalName``, ...) or
        a unique field. The first match wins when several match.

        Reconcile is **write-idempotent**: with ``on_conflict="update"`` (the
        default) a property is only written when the loaded value actually
        differs, so re-running an unchanged upsert queues no update at all. When
        the entity is missing the ``key`` and the requested properties are sent on
        the create. The reconcile is a client-side find-then-write, so it is not
        atomic — two racing writers can both miss and create; use a unique key (or
        the server-side ``Entity.upsert``) when that matters.

        Args:
            key: The property to match on (e.g. ``"uniqueName"``).
            value: The value identifying the entity.
            on_conflict: ``"update"`` (default) reconciles the existing entity;
                ``"skip"`` leaves it untouched (create-only-if-missing).
            **properties: The desired property values to create/reconcile with.

        Returns:
            The existing or newly created entity, populated after execution.

        Note:
            This is the portable, client-side path that works on Microsoft Graph
            and SharePoint alike. Endpoints that implement the Graph ``upsert``
            pattern can instead be written with a single server round-trip via
            :meth:`~office365.entity.Entity.upsert` on an alternate-key-addressed
            entity (``client.groups.get_by_alternate_key(...).upsert()``).

            Many collections also ship a typed ``ensure_<noun>`` helper for their
            natural key (``client.applications.ensure(...)``,
            ``web.ensure_folder_path(...)``, ``list.ensure_field(...)``); those are
            create-if-missing by default and delegate to the same primitive.
        """
        from office365.runtime.odata.literals import odata_literal
        from office365.runtime.queries.create_entity import CreateEntityQuery
        from office365.runtime.queries.get_or_create import get_or_create

        return_type = self.first_or_none(f"{key} eq {odata_literal(value)}")

        def _reconcile(entity: ClientObjectT) -> None:
            changed = {name: val for name, val in properties.items() if entity.get_property(name) != val}
            if not changed:
                return
            for name, val in changed.items():
                entity.set_property(name, val)
            cast("_UpdatableEntity", entity).update()

        return get_or_create(
            find=lambda: return_type,
            create_query=lambda: CreateEntityQuery(self, {key: value, **properties}, return_type),
            return_type=return_type,
            missing=lambda entity: not entity.is_loaded,
            on_conflict=on_conflict,
            reconcile=_reconcile,
        )

    # ── Import: deferred (queue-all) ─────────────────────────────

    def queue_records(self, records: List[dict], progress: "ProgressCallback | None" = None) -> Self:
        """Queue a create per record (deferred, run with ``execute_query()``).

        The neutral queue-all counterpart of :meth:`to_records`. Records are
        normalized to the item type and each becomes an entity queued for
        creation. Use the streaming :meth:`from_records` for large or
        resumable/idempotent imports (bounded memory).
        """
        from office365.runtime.converters.csv_reader import coerce_records

        return self._import_records(coerce_records(self._item_type, records), progress=progress)

    def queue_dataframe(self, df, progress: "ProgressCallback | None" = None) -> Self:
        """Queue a create per DataFrame row (deferred, run with ``execute_query()``)."""
        return self.queue_records(registry.reader_for("dataframe")(df), progress=progress)

    def _import_records(self, records: List[dict], progress: "ProgressCallback | None" = None) -> Self:
        """Queue a create per record, appending the pending entities to this collection."""
        from office365.runtime.operations import query_progress_hook
        from office365.runtime.queries.create_entity import CreateEntityQuery

        hook = query_progress_hook(len(records), progress) if callable(progress) else None
        for record in records:
            entity = self.create_typed_object(record)
            self.add_child(entity)
            qry = CreateEntityQuery(self, entity, entity)
            self.context.add_query(qry)
            if hook is not None:
                self.context.after_execute(hook)
        return self

    # ── Import: streaming (bounded, resumable, idempotent) ───────

    def from_records(
        self,
        source: Any,
        *,
        format: str = "records",  # noqa: A002
        chunksize: int = SAFE_PAGE_SIZE,
        key: "str | list[str] | None" = None,
        key_field: str = "MigrationKey",
        on_conflict: str = "skip",
        enforce_unique: bool = False,
        checkpoint: "ImportCheckpoint | CheckpointStore | str | PathLike | None" = None,
        on_error: str = "raise",
        progress: "ProgressCallback | None" = None,
        prepare: "Callable[[Any], None] | None" = None,
        before_chunk: "Callable[[Any], None] | None" = None,
        to_records: "Callable[[Any], list[dict]] | None" = None,
        total: Optional[int] = None,
        dry_run: bool = False,
        dead_letter: "str | PathLike | None" = None,
        mapping: "Dict[str, str] | None" = None,
        coerce: "Dict[str, Callable[[Any], Any]] | None" = None,
    ) -> "ImportResult":
        """Stream a source into this collection, memory-bounded (the streaming entry).

        ``source`` is chunked by ``format``: ``dataframe``/``csv`` (a DataFrame,
        chunk iterable, or CSV path/URL/file), ``records`` (an iterable of record
        batches), or any registered format (read whole). Returns an
        :class:`~office365.runtime.imports.ImportResult`; choose the terminal
        (``execute_query``/``execute_batch``) or iterate it. ``key`` enables
        idempotent skip/upsert via :meth:`upsert_target`; ``mapping`` renames
        source columns/keys; ``coerce`` maps a record key to a value converter
        (used for typed destination fields).
        """
        from office365.runtime.imports import ImportResult

        chunks, convert, inferred_total = self._resolve_source(source, format, chunksize, to_records)
        if total is None:
            total = inferred_total
        if mapping:
            convert = _apply_mapping(convert, mapping)

        raw_key_columns = [key] if isinstance(key, str) else (list(key) if key else [])
        key_columns = [self._key_column(c) for c in raw_key_columns]
        target = self.upsert_target(key_field=key_field, enforce_unique=enforce_unique) if key_columns else None
        if key_columns and target is None:
            raise ValueError("key= requires an upsert-capable collection (override upsert_target())")
        existing: Dict[str, Any] = {}
        keys_loaded = False

        def _prepare(first_chunk: Any) -> None:
            if callable(prepare):
                prepare(first_chunk)

        def _ensure_keys() -> None:
            """Ensure the key column and load existing keys (once, on every run).

            Loading is lazy (on the first queued chunk) rather than part of the
            fresh-run-only ``prepare`` so a **resumed** run still skips records
            that are already present — the key load is what makes a replayed or
            overlapping chunk idempotent, not just a fresh run.
            """
            nonlocal keys_loaded
            if target is None or keys_loaded:
                return
            target.ensure_key_field()
            self.context.execute_query()
            existing.update(target.load_keys())
            keys_loaded = True

        def _queue(records: list[dict]) -> tuple[int, int]:
            if coerce:
                records = [
                    {
                        key: (coerce[key](value) if key in coerce and value is not None else value)
                        for key, value in record.items()
                    }
                    for record in records
                ]
            if target is None:
                if not dry_run:
                    self.queue_records(records)
                return len(records), 0
            from office365.runtime.converters.upsert import keyed_queue

            _ensure_keys()
            return keyed_queue(
                target,
                records,
                key_columns=key_columns,
                existing=existing,
                on_conflict=on_conflict,
                dry_run=dry_run,
            )

        return ImportResult(
            self.context,
            self,
            chunks,
            to_records=convert,
            prepare=_prepare,
            before_chunk=before_chunk,
            queue=_queue,
            total=total,
            progress=progress,
            checkpoint=checkpoint,
            on_error=on_error,
            dry_run=dry_run,
            dead_letter=dead_letter,
            signature={
                "format": format,
                "chunk_size": chunksize,
                "key": list(key_columns),
                "key_field": key_field,
            },
        )

    def from_dataframe(self, df, **opts: Any) -> "ImportResult":
        """Stream a pandas DataFrame (or chunked CSV) into this collection."""
        return self.from_records(df, format="dataframe", **opts)

    def from_csv(self, source: Any, **opts: Any) -> "ImportResult":
        """Stream a CSV source (path/URL/file or chunk iterable) into this collection."""
        return self.from_records(source, format="csv", **opts)

    def from_json(self, source: Any, **opts: Any) -> "ImportResult":
        """Stream a JSON-array file into this collection."""
        return self.from_records(source, format="json", **opts)

    def from_ndjson(self, source: Any, **opts: Any) -> "ImportResult":
        """Stream an NDJSON (JSON Lines) source into this collection."""
        return self.from_records(source, format="ndjson", **opts)

    def from_excel(self, source: Any, **opts: Any) -> "ImportResult":
        """Stream an Excel (.xlsx) worksheet into this collection."""
        return self.from_records(source, format="excel", **opts)

    def from_parquet(self, source: Any, **opts: Any) -> "ImportResult":
        """Stream a Parquet file into this collection (requires the ``[parquet]`` extra)."""
        return self.from_records(source, format="parquet", **opts)

    def from_orc(self, source: Any, **opts: Any) -> "ImportResult":
        """Stream an ORC file into this collection (requires the ``[parquet]`` extra)."""
        return self.from_records(source, format="orc", **opts)

    def from_feather(self, source: Any, **opts: Any) -> "ImportResult":
        """Stream a Feather file into this collection (requires the ``[parquet]`` extra)."""
        return self.from_records(source, format="feather", **opts)

    def from_sql(self, source: Any, *, query: str, chunksize: int = 2000, **opts: Any) -> "ImportResult":
        """Stream a SQL query result into this collection (requires the ``[sql]`` extra).

        ``source`` is a SQLAlchemy ``Engine``/``Connection`` or a connection URL
        string; rows are fetched in ``chunksize`` batches (bounded memory).
        """
        from office365.runtime.converters.sql import sql_chunks

        return self.from_records(sql_chunks(source, query, chunksize), format="records", **opts)

    def from_duckdb(self, source: Any, *, query: str, chunksize: int = 2000, **opts: Any) -> "ImportResult":
        """Stream a DuckDB query result into this collection (requires the ``[duckdb]`` extra).

        ``source`` is a DuckDB connection or a database path; rows are fetched in
        ``chunksize`` batches (bounded memory).
        """
        from office365.runtime.converters.sql import duckdb_chunks

        return self.from_records(duckdb_chunks(source, query, chunksize), format="records", **opts)

    # ── Verification ─────────────────────────────────────────────

    def verify_keys(self, keys: Iterable[str], *, key_field: str = "MigrationKey") -> VerificationReport:
        """Reconcile an import: assert every key hash exists in the target.

        Uses the same keyed lookup as upsert (loads existing keys once), so it
        verifies that an idempotent import actually landed every record.
        """
        target = self.upsert_target(key_field=key_field)
        if target is None:
            raise ValueError("verify_keys requires an upsert-capable collection")
        existing = target.load_keys()
        keys = list(keys)
        missing = [key for key in keys if key not in existing]
        return VerificationReport(
            source_count=len(keys), target_count=len(keys) - len(missing), checked=len(keys), missing=missing
        )

    def verify(
        self,
        source: Any,
        *,
        key: "str | list[str]",
        format: str = "dataframe",  # noqa: A002
        key_field: str = "MigrationKey",
        to_records: "Callable[[Any], list[dict]] | None" = None,
    ) -> VerificationReport:
        """Reconcile a source's natural keys against this collection (bounded).

        Streams the source, hashes each record's natural key and checks it against
        the target's existing keys — the pipeline counterpart of the migration
        toolkit's ``verify``. Use ``List.verify(df, key=...)`` for a list.
        """
        from office365.runtime.converters.upsert import record_key

        raw = [key] if isinstance(key, str) else list(key)
        key_columns = [self._key_column(c) for c in raw]
        target = self.upsert_target(key_field=key_field)
        if target is None:
            raise ValueError("verify requires an upsert-capable collection")
        existing = target.load_keys()
        chunks, convert, _ = self._resolve_source(source, format, SAFE_PAGE_SIZE, to_records)
        checked = 0
        missing: list[str] = []
        for chunk in chunks:
            for record in convert(chunk):
                checked += 1
                if record_key(record, key_columns) not in existing:
                    missing.append(record_key(record, key_columns))
        return VerificationReport(
            source_count=checked, target_count=checked - len(missing), checked=checked, missing=missing
        )

    # ── Extension hooks ──────────────────────────────────────────

    def upsert_target(self, *, key_field: str = "MigrationKey", enforce_unique: bool = False) -> "UpsertTarget | None":
        """The keyed-import target, or ``None`` when the collection isn't keyable."""
        return None

    def _key_column(self, column: str) -> str:
        """Map a source column name to the record key used after import coercion."""
        return column

    def _resolve_source(
        self,
        source: Any,
        format: str,  # noqa: A002
        chunksize: int,
        to_records: "Callable[[Any], list[dict]] | None",
    ) -> "tuple[Iterable[Any], Callable[[Any], list[dict]], Optional[int]]":
        """Resolve ``(chunks, to_records, total)`` for a streaming import."""
        if format in ("dataframe", "csv"):
            from office365.runtime.converters.dataframe import dataframe_chunks, records_from_dataframe

            chunks, total = dataframe_chunks(source, chunksize)
            convert = to_records or (records_from_dataframe)
            return chunks, convert, total
        if format == "records":
            return source, (to_records or (lambda batch: batch)), None
        records = registry.reader_for(format)(source)
        return [records], (to_records or (lambda batch: batch)), len(records)
