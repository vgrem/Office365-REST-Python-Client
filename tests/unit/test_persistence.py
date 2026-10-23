"""Offline tests for crash-safe JSON persistence and checkpoint atomicity.

``atomic_write_json`` must guarantee that a reader (the next process resume)
never observes a truncated file: the target is only ever the old or the complete
new contents, even when serialization fails mid-write.
"""

from __future__ import annotations

import pytest
from office365.migration.base import MigrationPhase
from office365.migration.checkpoint import Checkpoint
from office365.runtime.imports import ImportCheckpoint
from office365.runtime.persistence import atomic_write_json, read_json


def _tmp_files(directory) -> list[str]:
    return [p.name for p in directory.iterdir() if p.name.endswith(".tmp")]


def test_atomic_write_creates_missing_parent_directories(tmp_path):
    target = tmp_path / "state" / "nested" / "checkpoint.json"
    atomic_write_json(target, {"ok": True})
    assert read_json(target) == {"ok": True}
    assert _tmp_files(target.parent) == []


def test_manifest_save_creates_missing_directories(tmp_path):
    from office365.migration.base import MigrationItem
    from office365.migration.manifest import Manifest

    path = tmp_path / "manifests" / "01-docs.manifest.json"
    Manifest([MigrationItem(source_path="/a/b.txt", dest_path="b.txt", item_type="file")]).save(path)

    assert Manifest.load(path).by_dest()["b.txt"].source_path == "/a/b.txt"
    assert _tmp_files(path.parent) == []


def test_import_checkpoint_round_trip_is_atomic(tmp_path):
    path = tmp_path / "import.json"
    checkpoint = ImportCheckpoint(cursor=10, chunks=2, errors=1, signature={"format": "csv"})
    checkpoint.save(path)
    assert _tmp_files(tmp_path) == []

    restored = ImportCheckpoint.load(path)
    assert restored.cursor == 10  # noqa: PLR2004
    assert restored.chunks == 2  # noqa: PLR2004
    assert restored.signature == {"format": "csv"}
    assert restored.updated_at  # stamped on save


def test_migration_checkpoint_round_trip_is_atomic(tmp_path):
    path = tmp_path / "migration.json"
    checkpoint = Checkpoint.create(run_id="run-1")
    checkpoint.phase = MigrationPhase.RUNNING
    checkpoint.source_watermark = "2026-01-01T00:00:00Z"
    checkpoint.items["/sites/a/file.txt"] = "done"
    checkpoint.save(path)

    assert _tmp_files(tmp_path) == []
    restored = Checkpoint.load(path)
    assert restored.run_id == "run-1"
    assert restored.phase == MigrationPhase.RUNNING
    assert restored.source_watermark == "2026-01-01T00:00:00Z"
    assert restored.items == {"/sites/a/file.txt": "done"}


def test_migration_checkpoint_save_keeps_previous_on_failure(tmp_path):
    path = tmp_path / "migration.json"
    Checkpoint.create(run_id="old").save(path)

    checkpoint = Checkpoint.create(run_id="new")
    checkpoint.items = {"bad": object()}  # type: ignore[dict-item]  # not JSON-serializable

    with pytest.raises(TypeError):
        checkpoint.save(path)

    assert Checkpoint.load(path).run_id == "old"
    assert _tmp_files(tmp_path) == []
