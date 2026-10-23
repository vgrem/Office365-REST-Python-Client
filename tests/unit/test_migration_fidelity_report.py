"""Tests for the fidelity report (what a run will and won't preserve)."""

from __future__ import annotations

import pytest
from office365.migration import MigrationJob, MigrationOptions, MigrationSession, describe_fidelity
from office365.migration.adapters.filesystem import FileSystemSource, FileSystemTarget


class _Source:
    def read_permissions(self, item):
        return []


class _Target:
    def apply_timestamps(self, item):
        pass

    def apply_permissions(self, item, permissions):
        pass


class _PlainSource:
    pass


class _PlainTarget:
    pass


def test_supported_requested_flags_are_preserved():
    options = MigrationOptions(preserve_timestamps=True, preserve_permissions=True)
    report = describe_fidelity(_Source(), _Target(), options)

    assert report.ok
    assert report.preserved == ["timestamps", "permissions"]
    assert report.unsupported == []


def test_unsupported_flag_is_reported_with_a_note():
    report = describe_fidelity(_PlainSource(), _PlainTarget(), MigrationOptions(preserve_timestamps=True))

    assert not report.ok
    assert report.unsupported == ["timestamps"]
    assert any("apply_timestamps" in note for note in report.notes)
    assert "UNSUPPORTED: timestamps" in report.summary()


def test_session_fidelity_is_empty_until_tasks_are_added(tmp_path):
    session = MigrationSession()

    assert session.fidelity() == []

    session.add_task(FileSystemSource(tmp_path), FileSystemTarget(tmp_path / "out"))

    entry = session.fidelity()[0]
    assert entry["ok"] is True
    assert entry["not_requested"] == ["timestamps", "permissions", "authorship", "versions"]


class _CountingSource:
    """Records whether planning got as far as enumerating."""

    def __init__(self):
        self.calls = 0

    def list_items(self, progress=None):
        self.calls += 1
        return []

    def close(self):
        pass


def test_plan_fails_before_enumerating_an_unhonorable_pair(tmp_path):
    # The point of failing at plan time: a half-million item enumeration is the
    # expensive part, and it must not run for a request the target cannot honor.
    source = _CountingSource()
    job = MigrationJob(source, FileSystemTarget(tmp_path / "out"), MigrationOptions(preserve_timestamps=True))

    with pytest.raises(NotImplementedError, match="preserve_timestamps"):
        job.plan()

    assert source.calls == 0


def test_plan_logs_the_forecast_matrix(caplog):
    source = _CountingSource()
    job = MigrationJob(source, FileSystemTarget("out"), MigrationOptions(preserve_authorship=True))

    with caplog.at_level("INFO", logger="office365.migration"):
        with pytest.raises(NotImplementedError):
            job.plan()

    record = next(r for r in caplog.records if getattr(r, "event", None) == "plan.fidelity")
    assert record.unsupported == ["authorship"]
    assert record.dimensions["content"] == "delivered"
    assert record.dimensions["versions"] == "unsupported"
    assert "authorship needs" in record.notes[0]


def test_the_report_persists_the_forecast(tmp_path):
    from office365.migration.report import build_report, export_reports

    source_dir = tmp_path / "src"
    source_dir.mkdir()
    (source_dir / "a.txt").write_text("x")
    job = MigrationJob(FileSystemSource(source_dir), FileSystemTarget(tmp_path / "out"), MigrationOptions())
    job.plan()
    job.run()

    report = build_report(job)

    row = report.summary[0]
    assert row["fidelity_ok"] is True
    assert "not requested: timestamps" in row["fidelity_summary"]
    statuses = {r["dimension"]: r["status"] for r in report.fidelity}
    assert statuses["content"] == "delivered"
    assert statuses["versions"] == "unsupported"
    note = next(r["note"] for r in report.fidelity if r["dimension"] == "versions")
    assert "version-preserving target" in note

    written = export_reports(job, tmp_path / "reports")
    assert (tmp_path / "reports" / "FidelityReport.csv").exists()
    assert any(path.endswith("FidelityReport.json") for path in written)
