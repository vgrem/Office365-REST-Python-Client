"""Tests for the SPMT-shaped migration session facade (offline)."""

from __future__ import annotations

import pytest
from office365.migration import MigrationOptions, MigrationSession, MigrationSettings, MigrationTask
from office365.migration.adapters.filesystem import FileSystemSource, FileSystemTarget


def test_session_constructor_options_override_settings(tmp_path):
    session = MigrationSession(options=MigrationOptions(preserve_permissions=True)).register(
        settings=MigrationSettings(preserve_timestamps=True)
    )

    job = session.add_task(FileSystemSource(tmp_path), FileSystemTarget(tmp_path / "out"))

    assert job.options.preserve_permissions is True
    assert job.options.preserve_timestamps is False


def test_task_round_trips_json():
    task = MigrationTask.file_share("C:/src", "https://x/sites/y", "Documents")
    assert MigrationTask.from_json(task.to_json()).file_share_source == "C:/src"


def test_session_cmdlets_with_direct_adapters(tmp_path):
    (tmp_path / "a.txt").write_text("hi", encoding="utf-8")
    session = MigrationSession().register()
    session.add_task(FileSystemSource(tmp_path), FileSystemTarget(tmp_path / "out"))

    assert [entry.id for entry in session.tasks] == ["1"]

    session.start()
    status = session.show()[0]
    assert status["id"] == "1"
    assert status["phase"] == "completed"
    assert status["stats"]["success"] == 1
    # the status carries the wall clock, so a caller (or a log consumer) can
    # derive a throughput without re-timing the run
    assert isinstance(status["duration_ms"], int)

    session.remove_task("1")
    assert session.tasks == []
    session.unregister()


def test_add_task_descriptor_requires_a_context():
    session = MigrationSession()
    with pytest.raises(ValueError, match="register a ClientContext"):
        session.add_task(file_share_source="C:/src", target_site_url="https://x", target_list="Documents")


def test_session_rejects_an_unknown_site_settings_mode():
    session = MigrationSession().register(settings=MigrationSettings(migrate_site_settings="ALL"))
    session._context = object()  # pyright: ignore[reportPrivateUsage]

    with pytest.raises(ValueError, match="unknown migrate_site_settings"):
        session.add_site_task(task=MigrationTask.sharepoint("https://x/sites/a", "https://x/sites/b", migrate_all=True))
