"""Delta re-run tests — drift between the persisted plan and a fresh plan."""

from __future__ import annotations

from office365.migration.base import ItemStatus, MigrationItem
from office365.migration.delta import DeltaReport, MovedItem, compute_delta
from office365.migration.job import MigrationJob


def _item(dest_path, **kwargs) -> MigrationItem:
    return MigrationItem(source_path=f"/src/{dest_path}", dest_path=dest_path, **kwargs)


class _PlanSource:
    """A source whose enumeration is swapped between calls (a drifting site)."""

    def __init__(self, items=None) -> None:
        self.items = list(items or [])
        self.warnings: list[str] = []

    def list_items(self, progress=None):
        return list(self.items)

    def label(self) -> str:
        return "plan-source"


class _Sink:
    """A minimal target: the delta is computed at plan time, so it never writes."""

    def list_paths(self):
        return []

    def exists(self, item):
        return False

    def write(self, item, payload):
        raise AssertionError("a plan-only test must not write")

    def commit(self):
        pass

    def modified(self, item):
        return None


def test_no_previous_plan_reports_no_baseline():
    report = compute_delta(None, [_item("a.txt")])

    assert report.baseline is None
    assert not report.has_baseline
    assert report.summary() == "delta: no previous plan"
    assert report.notes() == []
    assert report.is_empty


def test_unchanged_plan_is_an_empty_delta():
    items = [_item("a.txt", modified="2024-05-01T10:00:00Z")]
    report = compute_delta(items, items)

    assert report.baseline == 1
    assert report.is_empty
    assert not report.is_stale
    assert report.summary() == "delta vs 1 planned item(s): 0 new, 0 gone, 0 moved, 0 changed"


def test_detects_added_and_missing():
    previous = [_item("a.txt"), _item("folder/", item_type="folder")]
    current = [_item("a.txt"), _item("b.txt")]

    report = compute_delta(previous, current)

    assert report.added == ["b.txt"]
    assert report.missing == ["folder/"]
    assert report.moved == []
    assert report.is_stale


def test_identity_turns_a_missing_path_into_a_move():
    previous = [_item("a.txt", source_id="uid-1")]
    current = [_item("renamed/a.txt", source_id="uid-1")]

    report = compute_delta(previous, current)

    assert report.missing == []
    assert report.added == []
    assert [move.label for move in report.moved] == ["a.txt -> renamed/a.txt"]
    assert report.moved[0].source_id == "uid-1"
    assert report.is_stale


def test_identity_wins_over_a_reused_path():
    # The identity reappeared at another path while a *different* source item now
    # occupies the old one: the previously planned item moved (the path alone would
    # read as unchanged).
    previous = [_item("a.txt", source_id="uid-1")]
    current = [_item("a.txt", source_id="uid-2"), _item("b.txt", source_id="uid-1")]

    report = compute_delta(previous, current)

    assert report.missing == []
    assert [move.label for move in report.moved] == ["a.txt -> b.txt"]
    assert report.added == []


def test_items_without_identity_are_reported_as_gone():
    # A folder carries no source identity, so a rename cannot be told from a
    # delete: it is named as gone (the honest reading) rather than guessed at.
    previous = [_item("Docs/", item_type="folder"), _item("Docs/a.txt", source_id="uid-1")]
    current = [_item("Shared/", item_type="folder"), _item("Shared/a.txt", source_id="uid-1")]

    report = compute_delta(previous, current)

    assert report.missing == ["Docs/"]
    assert report.added == ["Shared/"]
    assert [move.label for move in report.moved] == ["Docs/a.txt -> Shared/a.txt"]


def test_changed_content_is_reported_not_stale():
    previous = [_item("a.txt", modified="2024-05-01T10:00:00Z")]
    current = [_item("a.txt", modified="2024-06-01T10:00:00Z")]

    report = compute_delta(previous, current)

    assert report.changed == ["a.txt"]
    assert not report.is_stale


def test_missing_timestamps_are_not_treated_as_changes():
    report = compute_delta([_item("a.txt")], [_item("a.txt", modified="2024-06-01T10:00:00Z")])

    assert report.changed == []


def test_notes_truncate_and_explain():
    previous = [_item(f"gone-{index}.txt") for index in range(7)]
    current: list[MigrationItem] = []

    notes = compute_delta(previous, current).notes()

    assert len(notes) == 1
    assert "7 item(s) were planned by the previous run but are gone" in notes[0]
    assert "gone-0.txt" in notes[0]
    assert "and 2 more" in notes[0]


def test_unreadable_baseline_is_reported():
    report = compute_delta(None, [_item("a.txt")], note="the previous plan could not be read (boom)")

    assert report.baseline is None
    assert report.notes() == ["delta unavailable: the previous plan could not be read (boom)"]


def test_report_serializes_to_a_json_safe_dict():
    report = compute_delta([_item("a.txt", source_id="uid-1")], [_item("b.txt", source_id="uid-1")])

    assert report.to_dict() == {
        "baseline": 1,
        "note": None,
        "added": [],
        "missing": [],
        "moved": [{"source_id": "uid-1", "from": "a.txt", "to": "b.txt"}],
        "changed": [],
    }
    assert MovedItem("uid-1", "a.txt", "b.txt").label == "a.txt -> b.txt"


def test_thin_report_defaults_are_empty():
    report = DeltaReport()

    assert report.is_empty
    assert not report.has_baseline
    assert report.notes() == []


def test_plan_diffs_against_the_plan_a_previous_run_persisted(tmp_path):
    manifest_path = tmp_path / "manifest.json"
    source = _PlanSource([_item("a.txt", source_id="uid-1"), _item("b.txt", source_id="uid-2")])
    job = MigrationJob(source, _Sink(), manifest_path=manifest_path)

    first = job.plan()
    assert len(first) == 2  # noqa: PLR2004
    assert job.delta.baseline is None
    assert job.delta.notes() == []

    # The source drifted: b.txt was renamed and a.txt was deleted.
    source.items = [_item("b-renamed.txt", source_id="uid-2")]
    second = job.plan()

    assert len(second) == 1
    assert job.delta.baseline == 2  # noqa: PLR2004
    assert job.delta.missing == ["a.txt"]
    assert [move.label for move in job.delta.moved] == ["b.txt -> b-renamed.txt"]


def test_a_corrupt_manifest_does_not_block_replanning(tmp_path):
    manifest_path = tmp_path / "manifest.json"
    manifest_path.write_text("{not json", encoding="utf-8")
    source = _PlanSource([_item("a.txt")])
    job = MigrationJob(source, _Sink(), manifest_path=manifest_path)

    plan = job.plan()

    assert len(plan) == 1
    assert job.delta.baseline is None
    assert job.delta.note is not None
    assert "could not be read" in job.delta.note
    assert job.delta.notes()[0].startswith("delta unavailable:")


def test_delta_is_empty_without_a_manifest_path(tmp_path):
    job = MigrationJob(_PlanSource([_item("a.txt")]), _Sink())
    job.plan()
    job.plan()

    assert job.delta.baseline is None
    assert not job.delta.is_stale
    assert job.manifest.items[0].status == ItemStatus.PENDING
