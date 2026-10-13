"""Tests for key-based, idempotent record imports (skip / update)."""

from __future__ import annotations

import pytest
from office365.runtime.converters.upsert import keyed_queue, record_key


class _FakeTarget:
    """Minimal UpsertTarget capturing what gets queued."""

    def __init__(self, key_field: str = "MigrationKey") -> None:
        self._key_field = key_field
        self.created: list[dict] = []
        self.updated: list[tuple[int, dict]] = []

    @property
    def key_field(self) -> str:
        return self._key_field

    def ensure_key_field(self) -> None: ...

    def load_keys(self):
        return {}

    def create_records(self, records):
        self.created.extend(records)

    def update_record(self, item_id, record):
        self.updated.append((item_id, record))


def _queue(target, records, existing, *, on_conflict="skip", dry_run=False):
    return keyed_queue(
        target,
        records,
        key_columns=["Name_", "date"],
        existing=existing,
        on_conflict=on_conflict,
        dry_run=dry_run,
    )


def test_record_key_is_deterministic_and_key_sensitive():
    columns = ["Name_", "date"]
    a = record_key({"Name_": "AAPL", "date": "2013-02-08"}, columns)
    b = record_key({"date": "2013-02-08", "Name_": "AAPL"}, columns)
    c = record_key({"Name_": "MSFT", "date": "2013-02-08"}, columns)

    assert a == b  # record key order doesn't matter
    assert a != c  # different values -> different key
    assert len(a) == 64  # noqa: PLR2004 — sha-256 hex


def test_keyed_queue_skips_existing():
    target = _FakeTarget()
    records = [{"Name_": "AAPL", "date": "d1"}, {"Name_": "AAPL", "date": "d2"}]
    existing = {record_key(records[0], ["Name_", "date"]): 1}

    queued, skipped = _queue(target, records, existing)

    assert (queued, skipped) == (1, 1)
    assert len(target.created) == 1  # only the new row
    assert target.updated == []
    assert records[1]["MigrationKey"] == record_key(records[1], ["Name_", "date"])


def test_keyed_queue_upserts_existing():
    target = _FakeTarget()
    records = [{"Name_": "AAPL", "date": "d1"}, {"Name_": "AAPL", "date": "d2"}]
    existing = {record_key(records[0], ["Name_", "date"]): 7}

    queued, skipped = _queue(target, records, existing, on_conflict="update")

    assert (queued, skipped) == (2, 0)
    assert len(target.created) == 1  # the new row
    assert target.updated[0][0] == 7  # noqa: PLR2004 — the existing row id


def test_keyed_queue_dedupes_within_run():
    target = _FakeTarget()
    records = [{"Name_": "AAPL", "date": "d1"}, {"Name_": "AAPL", "date": "d1"}]

    queued, skipped = _queue(target, records, {})

    assert (queued, skipped) == (1, 1)
    assert len(target.created) == 1


def test_keyed_queue_dry_run_plans_without_writing():
    target = _FakeTarget()
    records = [{"Name_": "AAPL", "date": "d1"}, {"Name_": "AAPL", "date": "d2"}]
    existing = {record_key(records[0], ["Name_", "date"]): 1}

    queued, skipped = _queue(target, records, existing, dry_run=True)

    assert (queued, skipped) == (1, 1)
    assert target.created == []
    assert target.updated == []


def test_keyed_queue_rejects_unknown_conflict_mode():
    with pytest.raises(ValueError, match="on_conflict"):
        _queue(_FakeTarget(), [{"Name_": "AAPL", "date": "d1"}], {}, on_conflict="nope")
