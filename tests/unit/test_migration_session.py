"""Tests for the SPMT-shaped migration session facade (offline)."""

from __future__ import annotations

import pytest
from office365.migration import MigrationOptions, MigrationSession, MigrationSettings, MigrationTask
from office365.migration.adapters.filesystem import FileSystemSource, FileSystemTarget


def test_settings_map_to_options():
    settings = MigrationSettings(
        preserve_permissions=True,
        preserve_timestamps=True,
        skip_files_with_extension=["txt", ".mp3"],
        migrate_files_modified_after="2024-01-01T00:00:00",
    )
    concurrency = 4
    options = settings.to_options(concurrency=concurrency)

    assert options.preserve_permissions is True
    assert options.preserve_timestamps is True
    assert options.exclude_patterns == ["*.txt", "*.mp3"]
    assert options.modified_after == "2024-01-01T00:00:00"
    assert options.concurrency == concurrency  # overrides win


def test_session_constructor_options_override_settings(tmp_path):
    session = MigrationSession(options=MigrationOptions(preserve_permissions=True)).register(
        settings=MigrationSettings(preserve_timestamps=True)
    )

    job = session.add_task(FileSystemSource(tmp_path), FileSystemTarget(tmp_path / "out"))

    assert job.options.preserve_permissions is True
    assert job.options.preserve_timestamps is False


def test_task_from_json_file_share():
    task = MigrationTask.from_json(
        '{"SourcePath": "C:/src", "TargetPath": "https://x/sites/y", '
        '"TargetList": "Documents", "TargetListRelativePath": "sub"}'
    )
    assert task.kind == "FileShare"
    assert task.file_share_source == "C:/src"
    assert task.target_list == "Documents"
    assert task.target_list_relative_path == "sub"


def test_task_from_json_sharepoint_lists():
    task = MigrationTask.from_json(
        '{"SourcePath": "https://onprem/sites/a", "TargetPath": "https://x/sites/y", '
        '"Items": {"Lists": [{"SourceList": "L1", "TargetList": "L2"}]}}'
    )
    assert task.kind == "SharePoint"
    assert task.source_list == "L1"
    assert task.target_list == "L2"


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


def test_session_surfaces_adapter_warnings(tmp_path):
    source = FileSystemSource(tmp_path)
    source.warnings = ["skipped a file without a name"]
    target = FileSystemTarget(tmp_path / "out")
    target.warnings = ["could not preserve timestamps"]
    session = MigrationSession()
    session.add_task(source, target)

    assert session.warnings() == ["skipped a file without a name", "could not preserve timestamps"]

    fresh = MigrationSession()
    fresh.add_task(FileSystemSource(tmp_path), FileSystemTarget(tmp_path))
    assert fresh.warnings() == []


def test_session_rejects_an_unknown_site_settings_mode():
    session = MigrationSession().register(settings=MigrationSettings(migrate_site_settings="ALL"))
    session._context = object()  # pyright: ignore[reportPrivateUsage]

    with pytest.raises(ValueError, match="unknown migrate_site_settings"):
        session.add_site_task(task=MigrationTask.sharepoint("https://x/sites/a", "https://x/sites/b", migrate_all=True))
