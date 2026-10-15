"""Migration manifest — the persisted plan of items to move.

The manifest is the "what to migrate": a serializable list of
:class:`MigrationItem` (source/dest path, size, type). It is produced by
enumerating a :class:`DataSource` and persisted as JSON so a run can be
planned, audited, and resumed.
"""

from __future__ import annotations

import json
from collections.abc import Callable, Iterator
from pathlib import Path
from typing import TYPE_CHECKING

from office365.migration.base import ItemStatus, MigrationItem, item_from_dict, item_to_dict
from office365.runtime.persistence import atomic_write_json

if TYPE_CHECKING:
    from office365.runtime.operations import Progress


class Manifest:
    """A serializable plan of ``MigrationItem`` units."""

    def __init__(self, items: list[MigrationItem] | None = None) -> None:
        self._items: list[MigrationItem] = list(items or [])

    @classmethod
    def from_source(
        cls,
        source,
        progress: Callable[["Progress"], None] | None = None,
    ) -> "Manifest":
        """Enumerate a source into a manifest (with per-item progress)."""
        return cls(source.list_items(progress))

    def add(self, item: MigrationItem) -> "Manifest":
        self._items.append(item)
        return self

    @property
    def items(self) -> list[MigrationItem]:
        return self._items

    @property
    def pending(self) -> list[MigrationItem]:
        return [i for i in self._items if i.status == ItemStatus.PENDING]

    @property
    def failed(self) -> list[MigrationItem]:
        return [i for i in self._items if i.status == ItemStatus.FAILED]

    def by_dest(self) -> dict[str, MigrationItem]:
        return {i.dest_path: i for i in self._items}

    def __len__(self) -> int:
        return len(self._items)

    def __iter__(self) -> Iterator[MigrationItem]:
        return iter(self._items)

    def save(self, path: str | Path) -> None:
        """Persist the manifest as a JSON array of items, atomically.

        Uses the same crash-safe write-then-rename as the checkpoint, so a crash
        mid-save never leaves a truncated manifest, and missing parent
        directories are created.
        """
        atomic_write_json(path, [item_to_dict(i) for i in self._items])

    @classmethod
    def load(cls, path: str | Path) -> "Manifest":
        """Load a manifest previously persisted with :meth:`save`."""
        with open(path, "r", encoding="utf-8") as f:
            return cls([item_from_dict(d) for d in json.load(f)])
