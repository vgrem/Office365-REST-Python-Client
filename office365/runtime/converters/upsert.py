"""Key-based conflict resolution for record imports (destination-agnostic).

A natural key is hashed into a stable value stored on the destination; a target
implements :class:`UpsertTarget` to load existing keys and create/update records.
The same :func:`keyed_queue` drives every collection (and the migration toolkit),
so idempotent upsert is one implementation, not one per destination.
"""

from __future__ import annotations

import hashlib
import json
from typing import Any, Iterable, Mapping, MutableMapping, Protocol, runtime_checkable

ON_CONFLICT_MODES = ("skip", "update")


def record_key(record: dict, key_columns: Iterable[str]) -> str:
    """Deterministic hash key for a record's natural key column(s).

    Canonicalizes the key values as JSON and hashes them (SHA-256), so the key is
    stable across runs and safe to store in a text column regardless of the
    source values' length or characters.
    """
    values = [record.get(column) for column in key_columns]
    payload = json.dumps(values, default=str, ensure_ascii=False, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


@runtime_checkable
class UpsertTarget(Protocol):
    """Destination capability needed for keyed skip/upsert."""

    @property
    def key_field(self) -> str:
        """The column storing the derived key hash."""
        ...

    def ensure_key_field(self) -> None:
        """Queue creation of the key column if missing (does not execute)."""
        ...

    def load_keys(self) -> Mapping[str, Any]:
        """Return the existing ``{key: item_id}`` map (executes)."""
        ...

    def create_records(self, records: list[dict]) -> None:
        """Queue a create for each record."""
        ...

    def update_record(self, item_id: Any, record: dict) -> None:
        """Queue an update of an existing item."""
        ...


def keyed_queue(
    target: UpsertTarget,
    records: list[dict],
    *,
    key_columns: Iterable[str],
    existing: MutableMapping[str, Any],
    on_conflict: str = "skip",
    dry_run: bool = False,
) -> tuple[int, int]:
    """Queue a chunk with key-based conflict resolution.

    Each record's natural key is hashed into ``target.key_field``. Records whose
    key is already in ``existing`` are either skipped (``on_conflict="skip"``) or
    queued as an update (``on_conflict="update"``); the rest are created.
    ``existing`` is updated in place so duplicate keys within the same run are
    deduplicated too. With ``dry_run`` the counts are computed without queuing
    anything (a plan preview).

    Returns:
        ``(queued, skipped)`` — records queued (created or updated) and records
        skipped as already present.
    """
    if on_conflict not in ON_CONFLICT_MODES:
        raise ValueError(f"on_conflict must be one of {ON_CONFLICT_MODES}, got {on_conflict!r}")
    key_field = target.key_field
    creates: list[dict] = []
    updates: list[tuple[Any, dict]] = []
    skipped = 0
    for record in records:
        key = record_key(record, key_columns)
        record[key_field] = key
        if key in existing:
            item_id = existing[key]
            if item_id is not None and on_conflict == "update":
                updates.append((item_id, record))
            else:
                skipped += 1
            continue
        existing[key] = None  # created this run (id unknown) — dedupe later duplicates
        creates.append(record)
    if not dry_run:
        if creates:
            target.create_records(creates)
        for item_id, record in updates:
            target.update_record(item_id, record)
    return len(creates) + len(updates), skipped
