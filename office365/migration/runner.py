"""Migration runner — executes a manifest against source/target adapters.

Drives the checkpointed, idempotent item loop: reads each item from the source,
writes it to the target honoring the conflict-resolution policy, records the
per-item status in the checkpoint (persisted after each batch), and collects
:class:`MigrationStats`. Interruptions (pause/cancel) stop cleanly at the next
batch boundary and can be resumed from the checkpoint.

When a target batches its writes — ``concurrency > 1``, or a target whose single
``write`` is deferred until a flush (``deferred_writes``, e.g. the record target)
— items are written in chunks via the ``write_many`` hook (e.g. the SharePoint
library target): file bytes can't ride an OData batch, so throughput comes from
concurrency, paced by a shared rate limiter. Each chunk is flushed before its
items are recorded ``DONE``, so a checkpoint never runs ahead of the target.
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Callable, Iterable, cast

from office365.migration.adapters import DataTarget, resolve_dest
from office365.migration.base import (
    ConflictResolution,
    ItemStatus,
    MigrationItem,
    MigrationOptions,
    MigrationPhase,
    MigrationStats,
)
from office365.migration.checkpoint import Checkpoint
from office365.runtime.operations import emit_progress

if TYPE_CHECKING:
    from office365.runtime.operations import Progress


def _assert_fidelity_supported(options: MigrationOptions, source, target: DataTarget) -> None:
    """Reject fidelity flags the adapter pair cannot honor.

    ``preserve_versions`` always needs the server-side Migration API (REST can't
    restore version history). ``preserve_timestamps`` / ``preserve_authorship`` /
    ``preserve_permissions`` are applied client-side on a best-effort basis, but
    only when the adapters expose the matching optional hooks — failing fast beats
    silently migrating without the requested fidelity.
    """
    if options.preserve_versions and not (
        getattr(target, "supports_versions", False) and callable(getattr(source, "read_version_history", None))
    ):
        raise NotImplementedError(
            "preserve_versions is not supported by this adapter pair: REST cannot restore version "
            "history, and even a version-preserving target needs source.read_version_history(item). "
            "Use the server-side Migration API (MigrationServerJob / SharePointPackageTarget) or set "
            "preserve_versions to False."
        )
    if options.preserve_timestamps and not callable(getattr(target, "apply_timestamps", None)):
        raise NotImplementedError(
            "preserve_timestamps is not supported by this target: it does not implement apply_timestamps(item)."
        )
    if options.preserve_authorship and not (
        callable(getattr(target, "apply_authorship", None)) or getattr(target, "supports_authorship", False)
    ):
        raise NotImplementedError(
            "preserve_authorship is not supported by this target: it does not implement apply_authorship(item) "
            "nor advertise supports_authorship."
        )
    if options.preserve_permissions and not (
        callable(getattr(source, "read_permissions", None)) and callable(getattr(target, "apply_permissions", None))
    ):
        raise NotImplementedError(
            "preserve_permissions is not supported by this adapter pair: it needs "
            "source.read_permissions(item) and target.apply_permissions(item, permissions)."
        )


def _apply_fidelity(source, target: DataTarget, item: MigrationItem, options: MigrationOptions) -> None:
    """Best-effort fidelity after a successful write (timestamps / authorship / ACLs).

    Failures propagate (and are captured per-item by the caller) so a requested
    fidelity that couldn't be applied is visible and the item stays resumable.
    """
    if options.preserve_permissions:
        permissions = source.read_permissions(item)
        if permissions:
            _call_optional(target, "apply_permissions", item, permissions)
    if options.preserve_authorship:
        _call_optional(target, "apply_authorship", item)
    # Timestamps last: the authorship/ACL writes above touch the item and would
    # otherwise bump ``Modified`` past the value we are trying to restore.
    if options.preserve_timestamps:
        _call_optional(target, "apply_timestamps", item)
    # Whatever a hook only cached (authorship without timestamps) lands as one write
    # here — and is a no-op when the timestamps write already carried it. Before the
    # approval step, which has to stay last: a system update re-approves the item.
    _call_optional(target, "finalize_fidelity", item)
    # Content-approval state goes after the timestamps: a document's system update
    # re-approves it, and a moderation change cannot share a write with other
    # properties. Only a pair that can read *and* apply it takes this step.
    state_reader = getattr(source, "read_item_state", None)
    if callable(state_reader) and callable(getattr(target, "apply_item_state", None)):
        state = state_reader(item)
        if state:
            _call_optional(target, "apply_item_state", item, state)


class _Watermark:
    """Incremental watermark — the highest source ``modified`` migrated so far.

    Persisted in ``Checkpoint.source_watermark``: a resumed incremental run skips
    every item at or below it, so only new/changed items are re-scanned.
    """

    def __init__(self, checkpoint: Checkpoint) -> None:
        self._checkpoint = checkpoint
        self._value = checkpoint.source_watermark

    @property
    def value(self) -> str | None:
        return self._value

    def is_stale(self, item: MigrationItem) -> bool:
        """Whether the item is at or below the watermark (already migrated)."""
        return self._value is not None and item.modified is not None and item.modified <= self._value

    def advance(self, item: MigrationItem) -> None:
        """Raise the watermark to the item's ``modified`` when it is newer."""
        if item.modified is not None and (self._value is None or item.modified > self._value):
            self._value = item.modified
            self._checkpoint.source_watermark = item.modified


class MigrationRunner:
    """Executes migration items between a source and a target adapter."""

    def run(
        self,
        source,
        target: DataTarget,
        items: Iterable[MigrationItem],
        options: MigrationOptions,
        checkpoint: Checkpoint,
        checkpoint_path: str | Path | None = None,
        progress: Callable[["Progress"], None] | None = None,
        stop_event: Callable[[], bool] | None = None,
    ) -> MigrationStats:
        _assert_fidelity_supported(options, source, target)
        # Let the target derive any per-run policy from the options before writes
        # start (e.g. a record target maps ``conflict_resolution`` -> ``on_conflict``).
        _call_optional(target, "configure", options)
        watermark = _Watermark(checkpoint) if options.incremental else None
        # Chunked writes are the norm whenever the target batches: parallel chunks
        # (``concurrency > 1``), or a target whose single ``write`` is deferred
        # until a flush (``deferred_writes`` — the record target queues creates).
        # Chunking keeps memory bounded and records ``DONE`` only after the chunk
        # is durable, so a crash cannot leave the checkpoint ahead of the target.
        chunked = (
            hasattr(target, "write_many")
            and options.conflict_resolution != ConflictResolution.RENAME
            and (options.concurrency > 1 or getattr(target, "deferred_writes", False))
        )
        # Folder fidelity is deferred: a folder's ``Modified`` follows its children, so
        # it can only be restored once everything inside it has been written.
        deferred: list[MigrationItem] = []
        if chunked:
            stats = self._run_parallel(
                source,
                target,
                items,
                options,
                checkpoint,
                checkpoint_path,
                progress,
                stop_event,
                watermark,
                deferred,
            )
        else:
            stats = self._run_sequential(
                source,
                target,
                items,
                options,
                checkpoint,
                checkpoint_path,
                progress,
                stop_event,
                watermark,
                deferred,
            )
        # Before ``commit``: a record target drops its pending per-item state there.
        self._apply_deferred_fidelity(source, target, deferred, options, checkpoint, stats)
        _call_optional(target, "commit", options)

        if checkpoint.phase != MigrationPhase.PAUSED:
            checkpoint.phase = MigrationPhase.COMPLETED if stats.errors == 0 else MigrationPhase.COMPLETED_WITH_ERRORS
        if checkpoint_path is not None:
            checkpoint.save(checkpoint_path)
        _call_optional(source, "close")
        _call_optional(target, "close")
        return stats

    @staticmethod
    def _apply_deferred_fidelity(
        source,
        target: DataTarget,
        items: list[MigrationItem],
        options: MigrationOptions,
        checkpoint: Checkpoint,
        stats: MigrationStats,
    ) -> None:
        """Apply fidelity to folders once all of their content exists.

        A folder's ``Modified`` follows its children: adding a file to it — or
        creating a subfolder — resets it to now. Restoring a folder's timestamps is
        therefore only meaningful after the whole run has written everything inside
        it, so the step is deferred past the content pass.
        """
        for item in items:
            try:
                _apply_fidelity(source, target, item, options)
            except Exception as e:  # noqa: BLE001 — per-item errors are captured, not fatal
                item.error = str(e)
                item.error_code = type(e).__name__
                checkpoint.record(item, ItemStatus.FAILED)
                # the folder itself was written, so it was counted as a success
                stats.success -= 1
                stats.errors += 1

    def _run_sequential(
        self,
        source,
        target: DataTarget,
        items: Iterable[MigrationItem],
        options: MigrationOptions,
        checkpoint: Checkpoint,
        checkpoint_path: str | Path | None,
        progress: Callable[["Progress"], None] | None,
        stop_event: Callable[[], bool] | None,
        watermark: _Watermark | None = None,
        deferred: list[MigrationItem] | None = None,
    ) -> MigrationStats:
        items = list(items)
        stats = MigrationStats(total=len(items))
        for index, item in enumerate(items):
            status = checkpoint.status_of(item)
            if status in (ItemStatus.DONE, ItemStatus.SKIPPED):
                stats.skipped += 1
                self._report_progress(progress, stats, item)
                continue
            if callable(stop_event) and stop_event():
                checkpoint.phase = MigrationPhase.PAUSED
                break
            if watermark is not None and watermark.is_stale(item):
                checkpoint.record(item, ItemStatus.SKIPPED)
                stats.skipped += 1
                self._report_progress(progress, stats, item)
                continue
            checkpoint.record(item, ItemStatus.IN_PROGRESS)
            try:
                if self._migrate(source, target, item, options, deferred):
                    checkpoint.record(item, ItemStatus.DONE)
                    stats.success += 1
                    stats.bytes_transferred += item.size_bytes
                    if watermark is not None:
                        watermark.advance(item)
                else:
                    checkpoint.record(item, ItemStatus.SKIPPED)
                    stats.skipped += 1
            except Exception as e:  # noqa: BLE001 — per-item errors are captured, not fatal
                item.error = str(e)
                item.error_code = type(e).__name__
                checkpoint.record(item, ItemStatus.FAILED)
                stats.errors += 1
            self._report_progress(progress, stats, item)
            if checkpoint_path is not None and (index + 1) % options.batch_size == 0:
                checkpoint.save(checkpoint_path)
        return stats

    def _run_parallel(
        self,
        source,
        target: DataTarget,
        items: Iterable[MigrationItem],
        options: MigrationOptions,
        checkpoint: Checkpoint,
        checkpoint_path: str | Path | None,
        progress: Callable[["Progress"], None] | None,
        stop_event: Callable[[], bool] | None,
        watermark: _Watermark | None = None,
        deferred: list[MigrationItem] | None = None,
    ) -> MigrationStats:
        items = list(items)
        stats = MigrationStats(total=len(items))
        chunk: list[MigrationItem] = []

        def _skip(item: MigrationItem) -> None:
            checkpoint.record(item, ItemStatus.SKIPPED)
            stats.skipped += 1
            self._report_progress(progress, stats, item)

        def _flush() -> None:
            if not chunk:
                return
            payloads = [source.read(item) for item in chunk]
            for item in chunk:
                _load_versions(source, target, item)
            failures = target.write_many(chunk, payloads, concurrency=options.concurrency)
            failed = {path: error for path, error in failures}
            for item in chunk:
                if item.dest_path in failed:
                    item.error = failed[item.dest_path]
                    item.error_code = "TransferError"
                    checkpoint.record(item, ItemStatus.FAILED)
                    stats.errors += 1
                else:
                    try:
                        _defer_or_apply_fidelity(source, target, item, options, deferred)
                    except Exception as e:  # noqa: BLE001 — per-item errors are captured, not fatal
                        item.error = str(e)
                        item.error_code = type(e).__name__
                        checkpoint.record(item, ItemStatus.FAILED)
                        stats.errors += 1
                    else:
                        checkpoint.record(item, ItemStatus.DONE)
                        stats.success += 1
                        stats.bytes_transferred += item.size_bytes
                        if watermark is not None:
                            watermark.advance(item)
                self._report_progress(progress, stats, item)
            chunk.clear()
            if checkpoint_path is not None:
                checkpoint.save(checkpoint_path)

        for item in items:
            status = checkpoint.status_of(item)
            if status in (ItemStatus.DONE, ItemStatus.SKIPPED):
                stats.skipped += 1
                self._report_progress(progress, stats, item)
                continue
            if callable(stop_event) and stop_event():
                checkpoint.phase = MigrationPhase.PAUSED
                break
            if (watermark is not None and watermark.is_stale(item)) or _outside_window(item, options):
                _skip(item)
                continue
            checkpoint.record(item, ItemStatus.IN_PROGRESS)
            if options.incremental and _target_up_to_date(source, target, item):
                _skip(item)
                continue
            if _excluded_by_conflict(target, item, options):
                checkpoint.record(item, ItemStatus.SKIPPED)
                stats.skipped += 1
                self._report_progress(progress, stats, item)
                continue
            chunk.append(item)
            if len(chunk) >= options.batch_size:
                _flush()
        _flush()
        return stats

    @staticmethod
    def _report_progress(progress, stats: MigrationStats, item: MigrationItem) -> None:
        processed = stats.success + stats.skipped + stats.errors
        emit_progress(progress, done=processed, total=stats.total, stage="migrating", items=[item])

    @staticmethod
    def _migrate(source, target: DataTarget, item: MigrationItem, options: MigrationOptions, deferred=None) -> bool:
        """Move one item; returns ``False`` when skipped (conflict/incremental/window)."""
        if _outside_window(item, options):
            return False
        if options.incremental and _target_up_to_date(source, target, item):
            return False
        if _excluded_by_conflict(target, item, options):
            return False
        dest = resolve_dest(item, target, options.conflict_resolution)
        item.dest_path = dest
        payload = source.read(item)
        _load_versions(source, target, item)
        target.write(item, payload)
        _defer_or_apply_fidelity(source, target, item, options, deferred)
        return True


def _excluded_by_conflict(target: DataTarget, item: MigrationItem, options: MigrationOptions) -> bool:
    """Whether an existing target item means "nothing to do" for a SKIP policy.

    A folder is never nothing to do: it holds no content to duplicate, and a resumed
    run has to re-apply its metadata (column values, timestamps, ACLs) to a folder
    that already exists just as much as to a fresh one.
    """
    if item.item_type == "folder":
        return False
    return options.conflict_resolution == ConflictResolution.SKIP and target.exists(item)


def _defer_or_apply_fidelity(
    source, target: DataTarget, item: MigrationItem, options: MigrationOptions, deferred: list[MigrationItem] | None
) -> None:
    """Apply the fidelity steps now, or queue the folder for the post-content pass."""
    if deferred is not None and item.item_type == "folder":
        deferred.append(item)
        return
    _apply_fidelity(source, target, item, options)


def _load_versions(source, target: DataTarget, item: MigrationItem) -> None:
    """Populate ``item.version_label`` / ``item.versions`` for a version-preserving target.

    No-op unless the target advertises ``supports_versions`` and the source exposes
    the optional ``read_version_history`` hook. Version bytes are transient — they
    live only on the in-flight item and are never checkpointed.
    """
    if not getattr(target, "supports_versions", False):
        return
    read = getattr(source, "read_version_history", None)
    if not callable(read):
        return
    label, older = cast("tuple[str | None, list[tuple[str, bytes]]]", read(item))
    item.version_label, item.versions = label, older


def _outside_window(item: MigrationItem, options: MigrationOptions) -> bool:
    """Whether the item is outside the ``created_after``/``modified_after`` window (skip it)."""
    if options.modified_after and item.modified is not None and item.modified <= options.modified_after:
        return True
    return bool(options.created_after and item.created is not None and item.created <= options.created_after)


def _target_up_to_date(source, target: DataTarget, item: MigrationItem) -> bool:
    """Incremental check: skip when the target is at least as new as the source."""
    if item.modified is None:
        return False
    target_modified = getattr(target, "modified", None)
    if not callable(target_modified) or not target.exists(item):
        return False
    target_value = target_modified(item)
    return target_value is not None and str(target_value) >= item.modified


def _call_optional(adapter, method: str, *args) -> None:
    """Invoke an optional adapter hook (``commit`` / ``close``) if present."""
    hook = getattr(adapter, method, None)
    if callable(hook):
        hook(*args)
