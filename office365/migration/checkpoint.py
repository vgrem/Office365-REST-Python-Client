"""Migration checkpoint — the persisted run state enabling resume.

A checkpoint records the job's phase, an optional source watermark (for
incremental migrations), and the per-item status for every item in the
manifest. The runner persists it after each batch, so an interrupted or failed
run can resume by re-driving only ``pending`` / ``failed`` / ``in_progress``
items — a checkpointed, idempotent, at-least-once migration.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from pathlib import Path

from office365.migration.base import ItemStatus, MigrationItem, MigrationPhase
from office365.runtime.converters.scalars import utc_now_iso
from office365.runtime.persistence import atomic_write_json, read_json


@dataclass
class Checkpoint:
    """Run-state snapshot for a migration job."""

    run_id: str
    phase: MigrationPhase = MigrationPhase.CREATED
    updated_at: str = ""
    source_watermark: str | None = None
    items: dict[str, str] = field(default_factory=dict)  # dest_path -> ItemStatus.value

    @classmethod
    def create(cls, run_id: str | None = None) -> "Checkpoint":
        return cls(
            run_id=run_id or uuid.uuid4().hex[:12],
            phase=MigrationPhase.CREATED,
            updated_at=utc_now_iso(),
        )

    def status_of(self, item: MigrationItem) -> ItemStatus:
        return ItemStatus(self.items.get(item.dest_path, ItemStatus.PENDING.value))

    def record(self, item: MigrationItem, status: ItemStatus) -> None:
        self.items[item.dest_path] = status.value
        item.status = status
        self.updated_at = utc_now_iso()

    def done_count(self) -> int:
        return sum(1 for v in self.items.values() if v == ItemStatus.DONE.value)

    def save(self, path: str | Path) -> None:
        """Persist the checkpoint as JSON, atomically (crash-safe write-then-rename).

        A crash mid-save never leaves a truncated file, so a resumed run always
        reads either the previous or the complete new checkpoint.
        """
        atomic_write_json(
            path,
            {
                "run_id": self.run_id,
                "phase": self.phase.value,
                "updated_at": self.updated_at,
                "source_watermark": self.source_watermark,
                "items": self.items,
            },
        )

    @classmethod
    def load(cls, path: str | Path) -> "Checkpoint":
        """Load a checkpoint previously persisted with :meth:`save`."""
        data = read_json(path)
        return cls(
            run_id=data["run_id"],
            phase=MigrationPhase(data.get("phase", MigrationPhase.CREATED.value)),
            updated_at=data.get("updated_at", ""),
            source_watermark=data.get("source_watermark"),
            items=data.get("items", {}),
        )
