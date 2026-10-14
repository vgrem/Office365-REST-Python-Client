"""Tests for the fidelity report (what a run will and won't preserve)."""

from __future__ import annotations

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


def test_default_options_are_content_only():
    report = describe_fidelity(_PlainSource(), _PlainTarget(), MigrationOptions())

    assert report.ok
    assert report.preserved == []
    assert report.unsupported == []
    assert report.not_requested == ["timestamps", "permissions", "versions"]
    assert report.summary() == "not requested: timestamps, permissions, versions"


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


def test_permissions_need_both_ends():
    report = describe_fidelity(_Source(), _PlainTarget(), MigrationOptions(preserve_permissions=True))

    assert not report.ok
    assert report.unsupported == ["permissions"]


def test_versions_always_need_the_server_side_api():
    report = describe_fidelity(_Source(), _Target(), MigrationOptions(preserve_versions=True))

    assert not report.ok
    assert report.unsupported == ["versions"]
    assert any("Migration API" in note for note in report.notes)


def test_report_to_dict_is_serializable():
    report = describe_fidelity(_PlainSource(), _PlainTarget(), MigrationOptions(preserve_versions=True))

    assert report.to_dict() == {
        "preserved": [],
        "unsupported": ["versions"],
        "not_requested": ["timestamps", "permissions"],
        "notes": report.notes,
        "ok": False,
    }


def test_job_exposes_options_and_fidelity(tmp_path):
    source = FileSystemSource(tmp_path)
    target = FileSystemTarget(tmp_path / "out")
    options = MigrationOptions(preserve_timestamps=True)

    job = MigrationJob(source, target, options)

    assert job.options is options
    # the filesystem target has no apply_timestamps, so the request is honest
    assert job.fidelity().unsupported == ["timestamps"]


def test_session_fidelity_is_empty_until_tasks_are_added(tmp_path):
    session = MigrationSession()

    assert session.fidelity() == []

    session.add_task(FileSystemSource(tmp_path), FileSystemTarget(tmp_path / "out"))

    entry = session.fidelity()[0]
    assert entry["ok"] is True
    assert entry["not_requested"] == ["timestamps", "permissions", "versions"]
