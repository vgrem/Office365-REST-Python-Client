"""Merged unit tests (consolidated; see git history for originals)."""

from __future__ import annotations

import io
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest import mock

from office365.migration import (
    ConflictResolution,
    MigrationJob,
    MigrationOptions,
    MigrationPhase,
    MigrationServerJob,
    MigrationSession,
)
from office365.migration.adapters.filesystem import FileSystemSource, FileSystemTarget, JsonFileSource, JsonFileTarget
from office365.migration.base import ItemStatus, MigrationItem, Principal
from office365.migration.checkpoint import Checkpoint
from office365.migration.runner import MigrationRunner, _apply_fidelity
from office365.migration.sharepoint.transfer import _transfer_files_parallel
from office365.runtime.types.event_handler import EventHandler
from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.folders.folder import Folder
from office365.sharepoint.utilities.move_copy_util import MoveCopyUtil


def _seed_tree(root) -> None:
    (root / "docs").mkdir(parents=True)
    (root / "docs" / "a.txt").write_text("alpha")
    (root / "docs" / "sub").mkdir()
    (root / "docs" / "sub" / "b.txt").write_text("beta")
    (root / "img.png").write_bytes(b"\x89PNG")


class _FlakySource(FileSystemSource):
    """A source that fails to read a specific item once."""

    def __init__(self, root, fail_on):
        super().__init__(root)
        self._fail_on = fail_on

    def read(self, item):
        if item.dest_path == self._fail_on:
            raise RuntimeError("transient read error")
        return super().read(item)


def test_filesystem_migration_completes(tmp_path):
    src, dst = tmp_path / "src", tmp_path / "dst"
    _seed_tree(src)

    job = MigrationJob(FileSystemSource(src), FileSystemTarget(dst))
    manifest = job.plan()

    assert len(manifest) == 3  # noqa: PLR2004
    stats = job.run()
    assert stats.errors == 0
    assert stats.success == 3  # noqa: PLR2004
    assert (dst / "docs" / "a.txt").read_text() == "alpha"
    assert (dst / "img.png").read_bytes() == b"\x89PNG"
    assert job.verify().ok


def test_checkpoint_resume_after_failure(tmp_path):
    src, dst = tmp_path / "src", tmp_path / "dst"
    _seed_tree(src)
    manifest_path = tmp_path / "manifest.json"
    checkpoint_path = tmp_path / "checkpoint.json"

    job = MigrationJob(
        _FlakySource(src, "docs/sub/b.txt"),
        FileSystemTarget(dst),
        manifest_path=manifest_path,
        checkpoint_path=checkpoint_path,
    )
    job.plan()
    stats = job.run()

    assert stats.success == 2  # noqa: PLR2004
    assert stats.errors == 1
    assert job.phase == MigrationPhase.COMPLETED_WITH_ERRORS

    # resume against the fixed source: only the failed item is re-driven
    job2 = MigrationJob(
        FileSystemSource(src),
        FileSystemTarget(dst),
        manifest_path=manifest_path,
        checkpoint_path=checkpoint_path,
    )
    stats2 = job2.resume()

    assert stats2.errors == 0
    assert stats2.success == 1
    assert (dst / "docs" / "sub" / "b.txt").read_text() == "beta"
    assert job2.verify().ok


def test_skip_conflict_is_idempotent(tmp_path):
    src, dst = tmp_path / "src", tmp_path / "dst"
    _seed_tree(src)
    (dst / "docs").mkdir(parents=True)
    (dst / "docs" / "a.txt").write_text("already here")

    job = MigrationJob(FileSystemSource(src), FileSystemTarget(dst))
    job.plan()
    stats = job.run()

    assert stats.skipped == 1  # noqa: PLR2004
    assert stats.success == 2  # noqa: PLR2004
    assert (dst / "docs" / "a.txt").read_text() == "already here"  # untouched


def test_conflict_overwrite(tmp_path):
    src, dst = tmp_path / "src", tmp_path / "dst"
    _seed_tree(src)
    dst.mkdir(parents=True, exist_ok=True)
    (dst / "img.png").write_bytes(b"old")

    job = MigrationJob(
        FileSystemSource(src),
        FileSystemTarget(dst),
        options=MigrationOptions(conflict_resolution=ConflictResolution.OVERWRITE),
    )
    job.plan()
    job.run()

    assert (dst / "img.png").read_bytes() == b"\x89PNG"


def test_conflict_rename(tmp_path):
    src, dst = tmp_path / "src", tmp_path / "dst"
    _seed_tree(src)
    dst.mkdir(parents=True, exist_ok=True)
    (dst / "img.png").write_bytes(b"existing")

    job = MigrationJob(
        FileSystemSource(src),
        FileSystemTarget(dst),
        options=MigrationOptions(conflict_resolution=ConflictResolution.RENAME),
    )
    job.plan()
    stats = job.run()

    assert stats.success == 3  # noqa: PLR2004
    assert (dst / "img-1.png").exists()


def test_conflict_to_on_conflict_mapping():
    from office365.migration.base import conflict_to_on_conflict

    assert conflict_to_on_conflict(ConflictResolution.OVERWRITE) == "update"
    assert conflict_to_on_conflict(ConflictResolution.SKIP) == "skip"
    assert conflict_to_on_conflict(ConflictResolution.RENAME) == "skip"  # records are keyed, not pathed


def test_list_target_derives_on_conflict_from_options():
    from office365.migration.sharepoint.adapters import SharePointListTarget

    target = SharePointListTarget(mock.Mock(), key="Title")
    assert target.on_conflict == "skip"  # default (no runner yet)

    target.configure(MigrationOptions(conflict_resolution=ConflictResolution.OVERWRITE))
    assert target.on_conflict == "update"

    target.configure(MigrationOptions(conflict_resolution=ConflictResolution.RENAME))
    assert target.on_conflict == "skip"


def test_list_target_explicit_on_conflict_wins():
    from office365.migration.sharepoint.adapters import SharePointListTarget

    target = SharePointListTarget(mock.Mock(), key="Title", on_conflict="update")
    target.configure(MigrationOptions(conflict_resolution=ConflictResolution.SKIP))
    assert target.on_conflict == "update"


def test_runner_configures_target_with_options():
    items = [MigrationItem(source_path="/s", dest_path="f.txt")]

    class _ConfigurableTarget(_FakeTarget):
        def __init__(self):
            super().__init__()
            self.configured_with = None

        def configure(self, options):
            self.configured_with = options

    source = _FakeSource(items)
    target = _ConfigurableTarget()
    options = MigrationOptions(concurrency=2, batch_size=100)

    MigrationRunner().run(source, target, items, options, Checkpoint.create())  # type: ignore[arg-type]

    assert target.configured_with is options


def test_pause_then_resume(tmp_path):
    src, dst = tmp_path / "src", tmp_path / "dst"
    src.mkdir(parents=True)
    for i in range(20):  # noqa: PLR2004
        (src / f"f{i:02}.txt").write_text(f"content {i}")

    job = MigrationJob(FileSystemSource(src), FileSystemTarget(dst))
    job.plan()

    paused = []

    def progress(p):
        if p.done >= 5 and not paused:  # noqa: PLR2004
            paused.append(True)
            job.pause()

    job.run(progress=progress)

    assert job.phase == MigrationPhase.PAUSED
    migrated = len(list(dst.rglob("*.txt")))
    assert 5 <= migrated < 20  # noqa: PLR2004

    job.resume()
    assert job.phase == MigrationPhase.COMPLETED
    assert job.stats.errors == 0
    assert len(list(dst.rglob("*.txt"))) == 20  # noqa: PLR2004


def test_export_reports_csv_and_json(tmp_path):
    import json as jsonlib

    src, dst = tmp_path / "src", tmp_path / "dst"
    _seed_tree(src)
    job = MigrationJob(FileSystemSource(src), FileSystemTarget(dst))
    job.plan()
    job.run()

    out = tmp_path / "reports"
    job.export_reports(out)

    assert (out / "SummaryReport.csv").exists()
    assert (out / "ItemReport.csv").exists()
    assert (out / "FailureReport.csv").exists() is False  # no failures
    assert (out / "SummaryReport.json").exists()

    summary = jsonlib.loads((out / "SummaryReport.json").read_text())
    assert summary[0]["total_items"] == 3  # noqa: PLR2004
    assert summary[0]["success"] == 3  # noqa: PLR2004
    assert summary[0]["errors"] == 0
    assert summary[0]["duration_secs"] >= 0
    assert job.duration is not None

    items = jsonlib.loads((out / "ItemReport.json").read_text())
    assert len(items) == 3  # noqa: PLR2004
    assert all(i["status"] == "done" for i in items)


def test_export_reports_failure(tmp_path):
    import json as jsonlib

    src, dst = tmp_path / "src", tmp_path / "dst"
    _seed_tree(src)
    job = MigrationJob(_FlakySource(src, "docs/sub/b.txt"), FileSystemTarget(dst))
    job.plan()
    job.run()

    out = tmp_path / "reports"
    job.export_reports(out)

    assert (out / "FailureReport.csv").exists()  # failures present
    failures = jsonlib.loads((out / "FailureReport.json").read_text())
    assert len(failures) == 1
    assert failures[0]["destination_path"] == "docs/sub/b.txt"
    assert "transient read error" in failures[0]["error"]


def test_incremental_skips_up_to_date_target(tmp_path):
    src, dst = tmp_path / "src", tmp_path / "dst"
    _seed_tree(src)
    job = MigrationJob(FileSystemSource(src), FileSystemTarget(dst))
    job.plan()
    job.run()
    assert job.stats.success == 3  # noqa: PLR2004

    # re-run incrementally: the target is at least as new as the source -> all skipped
    job2 = MigrationJob(
        FileSystemSource(src),
        FileSystemTarget(dst),
        options=MigrationOptions(incremental=True, conflict_resolution=ConflictResolution.OVERWRITE),
    )
    job2.plan()
    stats2 = job2.run()
    assert stats2.skipped == 3  # noqa: PLR2004
    assert stats2.success == 0


def test_incremental_migrates_changed_source(tmp_path):
    import time

    src, dst = tmp_path / "src", tmp_path / "dst"
    _seed_tree(src)
    job = MigrationJob(FileSystemSource(src), FileSystemTarget(dst))
    job.plan()
    job.run()

    time.sleep(1.1)  # ensure the modified source file is strictly newer
    (src / "img.png").write_bytes(b"newer content")

    job2 = MigrationJob(
        FileSystemSource(src),
        FileSystemTarget(dst),
        options=MigrationOptions(incremental=True, conflict_resolution=ConflictResolution.OVERWRITE),
    )
    job2.plan()
    stats2 = job2.run()
    assert stats2.success == 1
    assert stats2.skipped == 2  # noqa: PLR2004


def test_json_records_round_trip(tmp_path):
    import json as jsonlib

    src = tmp_path / "json_src"
    src.mkdir()
    (src / "a.json").write_text(jsonlib.dumps({"name": "Alice"}, indent=2))
    (src / "b.json").write_text(jsonlib.dumps({"name": "Bob"}, indent=2))

    out = tmp_path / "json_dst"
    job = MigrationJob(JsonFileSource(src), JsonFileTarget(out))
    job.plan()
    stats = job.run()

    assert stats.success == 2  # noqa: PLR2004
    assert (out / "a.json").exists()
    assert jsonlib.loads((out / "a.json").read_text()) == {"name": "Alice"}
    assert job.verify().ok


def test_report_summary_is_enriched(tmp_path):
    import json as jsonlib

    src, dst = tmp_path / "src", tmp_path / "dst"
    _seed_tree(src)
    job = MigrationJob(FileSystemSource(src), FileSystemTarget(dst))
    job.plan()
    job.run()

    out = tmp_path / "reports"
    job.export_reports(out)
    summary = jsonlib.loads((out / "SummaryReport.json").read_text())[0]

    assert summary["total_bytes"] > 0
    assert summary["total_gb"] == round(summary["total_bytes"] / (1024**3), 2)
    assert summary["migrated_gb"] == summary["total_gb"]
    assert summary["not_migrated_gb"] == 0
    assert summary["items_not_migrated"] == 0
    assert summary["warnings"] == 0
    assert summary["run_id"]
    assert summary["gb_per_hour"] is not None

    item = jsonlib.loads((out / "ItemReport.json").read_text())[0]
    assert item["extension"]
    assert item["file_name"]
    assert item["error_code"] == ""


def test_report_author_id_is_the_principals_site_local_id(tmp_path):
    # The ItemReport column is a report-level convenience: the numeric id lives on
    # ``item.author`` (nothing else can hold a site-local id), and an item whose
    # author could not be resolved reports nothing rather than a stale number.
    from office365.migration.report import build_report

    src, dst = tmp_path / "src", tmp_path / "dst"
    _seed_tree(src)
    job = MigrationJob(FileSystemSource(src), FileSystemTarget(dst))
    job.plan()
    job.run()

    first, second = job.manifest.items[0], job.manifest.items[1]
    first.author = Principal("i:0#.f|membership|a@contoso.com", "1003200065102863", "Alice", user_id=7)
    second.author = None

    rows = build_report(job).items

    assert rows[0]["author_id"] == 7  # noqa: PLR2004
    assert rows[1]["author_id"] is None


def test_report_failure_carries_error_code(tmp_path):
    import json as jsonlib

    src, dst = tmp_path / "src", tmp_path / "dst"
    _seed_tree(src)
    job = MigrationJob(_FlakySource(src, "docs/sub/b.txt"), FileSystemTarget(dst))
    job.plan()
    job.run()

    out = tmp_path / "reports"
    job.export_reports(out)
    failures = jsonlib.loads((out / "FailureReport.json").read_text())
    assert failures[0]["error_code"] == "RuntimeError"
    assert "transient read error" in failures[0]["error"]

    summary = jsonlib.loads((out / "SummaryReport.json").read_text())[0]
    assert summary["errors"] == 1
    assert summary["items_not_migrated"] == 1


def test_progress_reaches_total_when_items_are_skipped(tmp_path):
    src, dst = tmp_path / "src", tmp_path / "dst"
    _seed_tree(src)
    (dst / "docs").mkdir(parents=True)
    (dst / "docs" / "a.txt").write_text("already here")  # conflict -> skipped

    seen = []

    def progress(p):
        seen.append((p.done, p.total, p.stage))

    job = MigrationJob(FileSystemSource(src), FileSystemTarget(dst))
    job.plan()
    stats = job.run(progress=progress)

    assert stats.total == 3  # noqa: PLR2004
    assert seen[-1][0] == stats.total  # the last emit reports full completion
    assert all(total is None or total == stats.total for _, total, _ in seen)


class _TreeSource:
    """A library-like source: file and folder items."""

    def __init__(self, items):
        self._items = items

    def label(self) -> str:
        return "tree"

    def list_items(self, progress=None):
        return list(self._items)

    def read(self, item):
        return b"" if item.item_type == "folder" else b"content"

    def checksum(self, item):
        import hashlib

        return hashlib.md5(self.read(item)).hexdigest()

    def close(self) -> None:
        pass


def test_folder_tree_with_empty_folders_preserved_and_verified(tmp_path):
    from office365.migration.base import MigrationItem

    dst = tmp_path / "dst"
    items = [
        MigrationItem("site/keep", "keep/", item_type="folder"),
        MigrationItem("site/keep/a.txt", "keep/a.txt", size_bytes=7, item_type="file"),
        MigrationItem("site/empty", "empty/", item_type="folder"),
    ]
    job = MigrationJob(
        _TreeSource(items),
        FileSystemTarget(dst, include_folders=True),
        options=MigrationOptions(conflict_resolution=ConflictResolution.OVERWRITE),
    )
    job.plan()
    stats = job.run()

    assert stats.errors == 0
    assert stats.success == 3  # noqa: PLR2004
    assert (dst / "keep" / "a.txt").read_text() == "content"
    assert (dst / "empty").is_dir()  # empty folder was created
    assert "keep/" in FileSystemTarget(dst, include_folders=True).list_paths()
    assert job.verify().ok


def test_filesystem_target_lists_folders_only_when_requested(tmp_path):
    from office365.migration.base import MigrationItem

    dst = tmp_path / "dst"
    target = FileSystemTarget(dst)
    target.write(MigrationItem("/x", "docs/sub/", item_type="folder"), b"")
    target.write(MigrationItem("/x", "docs/sub/a.txt", size_bytes=1, item_type="file"), b"a")

    assert target.list_paths() == ["docs/sub/a.txt"]  # default: files only
    folder_aware = FileSystemTarget(dst, include_folders=True)
    assert set(folder_aware.list_paths()) == {"docs/", "docs/sub/", "docs/sub/a.txt"}


def _tree(tmp_path):
    src = tmp_path / "src"
    dst = tmp_path / "dst"
    (src / "docs").mkdir(parents=True)
    (src / "docs" / "a.txt").write_text("alpha")
    (src / "b.txt").write_text("beta")
    return str(src), str(dst)


def test_session_lifecycle(tmp_path):
    src, dst = _tree(tmp_path)
    session = MigrationSession()

    job = session.add_task(
        FileSystemSource(src),
        FileSystemTarget(dst),
        options=MigrationOptions(conflict_resolution=ConflictResolution.OVERWRITE),
    )
    assert len(session.jobs) == 1
    assert job.source_label == src

    session.start()
    status = session.status()[0]
    assert status["phase"] == MigrationPhase.COMPLETED.value
    assert status["stats"]["success"] == 2  # noqa: PLR2004
    assert status["stats"]["errors"] == 0

    assert (Path(dst) / "b.txt").exists()
    assert (Path(dst) / "docs" / "a.txt").exists()

    session.stop()
    session.remove_task(job)
    session.unregister()
    assert session.jobs == []


def test_add_task_with_own_options(tmp_path):
    src, dst = _tree(tmp_path)
    session = MigrationSession()
    job = session.add_task(
        FileSystemSource(src),
        FileSystemTarget(dst),
        options=MigrationOptions(concurrency=2),
    )
    assert job._options.concurrency == 2  # noqa: SLF001, PLR2004


class _Result:
    def __init__(self, value):
        self.value = value

    def execute_query(self):
        return self


class TestMigrationServerJob(unittest.TestCase):
    def test_submit_returns_job_id(self):
        site = mock.Mock()
        site.create_migration_ingestion_job.return_value = _Result("job-123")

        job = MigrationServerJob(site)
        job_id = job.submit("web-1", "uri/src", "uri/manifest", "uri/queue")

        self.assertEqual(job_id, "job-123")
        site.create_migration_ingestion_job.assert_called_once()
        kwargs = site.create_migration_ingestion_job.call_args.kwargs
        self.assertEqual(kwargs["g_web_id"], "web-1")
        self.assertTrue(kwargs["ingestion_task_key"])

    def test_monitor_reports_progress_and_terminal(self):
        statuses = iter([("running", 1, 10), ("running", 5, 10), ("succeeded", 10, 10)])
        seen = []
        job = MigrationServerJob(mock.Mock())

        def status_fn(job_id):
            return next(statuses)

        result = job.monitor(
            "job-1",
            status_fn,
            interval=0.01,
            timeout=10,
            progress=lambda p: seen.append((p.done, p.total)),
        )

        self.assertEqual(result, "succeeded")
        self.assertEqual([s[0] for s in seen], [1, 5, 10])  # noqa: PLR2004
        self.assertEqual(seen[-1][1], 10)  # noqa: PLR2004

    def test_monitor_times_out(self):
        job = MigrationServerJob(mock.Mock())

        with self.assertRaises(TimeoutError):
            job.monitor("job-1", lambda jid: ("running", 1, None), interval=0.01, timeout=0.05)


class _File:
    def execute_query(self):
        return self

    def execute_query_retry(self, **kwargs):
        return self


class _Files:
    def __init__(self, log):
        self._log = log

    def upload(self, content, name):
        self._log.append(("upload", name))
        return _File()

    def create_upload_session(self, path, chunk_size=None, file_name=None):
        self._log.append(("session", file_name))
        return _File()

    def upload_content(self, content, file_name, chunk_size=4 * 1024 * 1024):
        if len(content) <= chunk_size:
            return self.upload(content, file_name)
        return self.create_upload_session(None, chunk_size=chunk_size, file_name=file_name)


class _Folder:
    def __init__(self, context, log):
        self.context = context
        self._log = log
        self._url = "/sites/x/Shared Documents"

    @property
    def server_relative_url(self):
        return self._url

    @property
    def folders(self):
        return self

    def ensure_by_path(self, rel):
        self._log.append(("ensure", rel))
        return self

    def ensure_folder(self, rel):
        return self.ensure_by_path(rel)

    def ensure_folders(self, paths):
        for rel in sorted(set(paths)):
            self.ensure_by_path(rel)
        return self

    @property
    def files(self):
        return _Files(self._log)

    def get(self):
        return self

    def execute_query(self):
        return self


class _Pending:
    beforeExecute = EventHandler()
    afterExecute = EventHandler()
    onError = EventHandler()
    transport = None  # never executed in these fakes

    def with_rate_limiter(self, limiter):
        return self


class _Context:
    base_url = "https://contoso.sharepoint.com/sites/x"

    def __init__(self, log):
        self._log = log

    def clone(self, url):
        return _Context(self._log)

    def pending_request(self):
        return _Pending()

    @property
    def web(self):
        return self

    def get_folder_by_server_relative_path(self, url):
        return _Folder(self, self._log)


class TestTransferFilesParallel(unittest.TestCase):
    def test_transfers_all_files_and_dedups_folders(self):
        log = []
        root = _Folder(_Context(log), log)
        failures = _transfer_files_parallel(
            root,  # type: ignore[arg-type]
            [("a.txt", b"x"), ("docs/b.txt", b"y"), ("docs/c.txt", b"z")],
            concurrency=4,
        )

        self.assertEqual(failures, [])
        self.assertEqual(log.count(("ensure", "docs")), 1)  # folder ensured once
        uploads = [entry for entry in log if entry[0] == "upload"]
        self.assertEqual(sorted(name for _, name in uploads), ["a.txt", "b.txt", "c.txt"])

    def test_large_files_use_upload_session(self):
        log = []
        root = _Folder(_Context(log), log)
        big = b"x" * (4 * 1024 * 1024 + 1)
        _transfer_files_parallel(root, [("big.bin", big)], concurrency=1)  # type: ignore[arg-type]
        self.assertIn(("session", "big.bin"), log)
        self.assertNotIn(("upload", "big.bin"), log)


class _FakeSource:
    def __init__(self, items):
        self._items = items
        self.payloads = {i.source_path: f"data-{i.source_path}" for i in items}

    def read(self, item):
        return self.payloads[item.source_path]

    def close(self):
        pass


class _FakeTarget:
    def __init__(self):
        self.written = []
        self.batches = []

    def exists(self, item):
        return False

    def write(self, item, payload):
        self.written.append((item.dest_path, payload))

    def write_many(self, items, payloads, concurrency=1):
        self.batches.append(len(items))
        self.written.extend((item.dest_path, payload) for item, payload in zip(items, payloads))
        return []

    def list_paths(self):
        return [p for p, _ in self.written]

    def checksum(self, item):
        return ""

    def commit(self, options=None):
        pass

    def close(self):
        pass


class TestRunnerParallel(unittest.TestCase):
    def _items(self, n: int):
        return [MigrationItem(source_path=f"/s{i}", dest_path=f"f{i}.txt") for i in range(n)]

    def test_parallel_chunks_by_batch_size(self):
        items = self._items(5)
        source = _FakeSource(items)
        target = _FakeTarget()
        options = MigrationOptions(concurrency=2, batch_size=2)
        checkpoint = Checkpoint.create()

        stats = MigrationRunner().run(source, target, items, options, checkpoint)  # type: ignore[arg-type]

        self.assertEqual(stats.total, 5)  # noqa: PLR2004
        self.assertEqual(stats.success, 5)  # noqa: PLR2004
        self.assertEqual(stats.errors, 0)
        self.assertEqual(target.batches, [2, 2, 1])  # chunked by batch_size
        statuses = [checkpoint.status_of(i) for i in items]
        self.assertEqual(set(statuses), {ItemStatus.DONE})

    def test_parallel_captures_write_failures(self):
        items = self._items(3)
        source = _FakeSource(items)

        class _Failing(_FakeTarget):
            def write_many(self, items, payloads, concurrency=1):
                return [(items[0].dest_path, "boom")]

        target = _Failing()
        options = MigrationOptions(concurrency=2, batch_size=100)
        stats = MigrationRunner().run(source, target, items, options, Checkpoint.create())  # type: ignore[arg-type]

        self.assertEqual(stats.errors, 1)
        self.assertEqual(stats.success, 2)  # noqa: PLR2004
        self.assertEqual(items[0].error, "boom")

    def test_folder_fidelity_is_applied_after_all_content(self):
        # A folder's ``Modified`` follows its children — uploading a file into it (or
        # creating a subfolder) resets it — so its timestamps can only be restored
        # once the whole content pass is done.
        calls: list[str] = []
        items = [
            MigrationItem("/s/Area", "Area/", item_type="folder"),
            MigrationItem("/s/Area/doc.txt", "Area/doc.txt"),
        ]
        source = _FakeSource(items)

        class _Target(_FakeTarget):
            def write(self, item, payload):
                calls.append(f"write:{item.dest_path}")
                super().write(item, payload)

            def apply_timestamps(self, item):
                calls.append(f"apply_timestamps:{item.dest_path}")

        stats = MigrationRunner().run(  # type: ignore[arg-type]
            source, _Target(), items, MigrationOptions(preserve_timestamps=True), Checkpoint.create()
        )

        self.assertEqual(stats.success, 2)  # noqa: PLR2004
        self.assertEqual(
            calls,
            [
                "write:Area/",
                "write:Area/doc.txt",
                "apply_timestamps:Area/doc.txt",
                "apply_timestamps:Area/",
            ],
        )

    def test_a_deferred_fidelity_failure_is_reported_against_its_folder(self):
        items = [MigrationItem("/s/Area", "Area/", item_type="folder")]
        source = _FakeSource(items)

        class _Target(_FakeTarget):
            def apply_timestamps(self, item):
                raise ValueError("You must specify a valid date")

        stats = MigrationRunner().run(  # type: ignore[arg-type]
            source, _Target(), items, MigrationOptions(preserve_timestamps=True), Checkpoint.create()
        )

        self.assertEqual((stats.success, stats.errors), (0, 1))
        self.assertEqual(items[0].error_code, "ValueError")


class TestRunnerExistingTargets(unittest.TestCase):
    """Skip-on-conflict versus folders: a folder's metadata is always re-applied."""

    def _run(self, items):
        class _Target(_FakeTarget):
            written = []

            def exists(self, item):
                return True

            def write(self, item, payload):
                self.written.append(item.dest_path)

            def apply_timestamps(self, item):
                self.written.append(f"timestamps:{item.dest_path}")

        target = _Target()
        stats = MigrationRunner().run(  # type: ignore[arg-type]
            _FakeSource(items), target, items, MigrationOptions(preserve_timestamps=True), Checkpoint.create()
        )
        return stats, target.written

    def test_an_existing_folder_is_reapplied_not_skipped(self):
        # A folder holds no content to duplicate, and a resumed run still has to
        # restore its metadata — otherwise a re-verify reports it as drifted.
        items = [MigrationItem("/s/Area", "Area/", item_type="folder")]

        stats, written = self._run(items)

        self.assertEqual(stats.success, 1)
        self.assertEqual(written, ["Area/", "timestamps:Area/"])

    def test_an_existing_file_is_still_skipped(self):
        items = [MigrationItem("/s/doc.txt", "doc.txt")]

        stats, written = self._run(items)

        self.assertEqual(stats.skipped, 1)
        self.assertEqual(written, [])


class TestApplyFidelity(unittest.TestCase):
    """Order of the post-write fidelity steps, and which optional hooks drive them."""

    def _options(self) -> MigrationOptions:
        return MigrationOptions(preserve_timestamps=True, preserve_authorship=True, preserve_permissions=True)

    def test_approval_state_is_applied_after_the_timestamp_write(self):
        # A document's system update re-approves the item, so approval has to be
        # restored last (and separately: a moderated document refuses to change
        # moderation together with other properties).
        calls: list[str] = []

        class _Source:
            def read_permissions(self, item):
                calls.append("read_permissions")
                return []

            def read_item_state(self, item):
                calls.append("read_item_state")
                return {"_ModerationStatus": "0"}

        class _Target:
            def apply_authorship(self, item):
                calls.append("apply_authorship")

            def apply_timestamps(self, item):
                calls.append("apply_timestamps")

            def finalize_fidelity(self, item):
                calls.append("finalize_fidelity")

            def apply_item_state(self, item, state):
                calls.append(f"apply_item_state:{state['_ModerationStatus']}")

        _apply_fidelity(_Source(), _Target(), MigrationItem("/s/doc", "doc"), self._options())

        self.assertEqual(calls[-1], "apply_item_state:0")
        self.assertLess(calls.index("apply_timestamps"), calls.index("finalize_fidelity"))
        self.assertLess(calls.index("finalize_fidelity"), calls.index("apply_item_state:0"))

    def test_an_approved_item_is_not_rewritten(self):
        calls: list[str] = []

        class _Source:
            def read_item_state(self, item):
                return None

        class _Target:
            def apply_item_state(self, item, state):
                calls.append("apply_item_state")

        _apply_fidelity(_Source(), _Target(), MigrationItem("/s/doc", "doc"), MigrationOptions())

        self.assertEqual(calls, [])

    def test_the_approval_step_needs_both_hooks(self):
        calls: list[str] = []

        class _Source:
            def read_item_state(self, item):
                calls.append("read_item_state")
                return {"_ModerationStatus": "0"}

        class _Target:
            pass

        _apply_fidelity(_Source(), _Target(), MigrationItem("/s/doc", "doc"), MigrationOptions())

        self.assertEqual(calls, [])


def uploadfolder__folder() -> Folder:
    ctx = ClientContext("https://contoso.sharepoint.com/sites/x")
    return ctx.web.root_folder


class TestUploadFolderEntries(unittest.TestCase):
    def test_directory_walk_preserves_structure(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "docs").mkdir()
            (root / "docs" / "a.txt").write_text("alpha")
            (root / "b.txt").write_text("beta")

            entries = MoveCopyUtil._collect_upload_entries(root, recursive=True)
            rels = sorted(rel for rel, _ in entries)
            self.assertEqual(rels, ["b.txt", "docs/a.txt"])
            self.assertEqual(dict(entries)["docs/a.txt"](), b"alpha")
            self.assertEqual(dict(entries)["b.txt"](), b"beta")

    def test_directory_walk_non_recursive_is_flat(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "docs").mkdir()
            (root / "docs" / "a.txt").write_text("alpha")
            (root / "b.txt").write_text("beta")

            entries = MoveCopyUtil._collect_upload_entries(root, recursive=False)
            self.assertEqual([rel for rel, _ in entries], ["b.txt"])

    def test_single_file_uses_name(self):
        with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False) as f:
            f.write("hello")
            path = Path(f.name)
        try:
            entries = MoveCopyUtil._collect_upload_entries(path, recursive=True)
            self.assertEqual([rel for rel, _ in entries], [path.name])
        finally:
            path.unlink()

    def test_list_of_file_paths_each_at_name(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            a = root / "a.txt"
            a.write_text("a")
            b = root / "b.txt"
            b.write_text("b")

            entries = MoveCopyUtil._collect_upload_entries([a, b], recursive=True)
            self.assertEqual(sorted(rel for rel, _ in entries), ["a.txt", "b.txt"])

    def test_content_pairs(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "x.bin"
            p.write_bytes(b"\x01\x02")
            entries = MoveCopyUtil._collect_upload_entries(
                [("f.txt", b"bytes"), ("t.txt", "text"), ("p.bin", p)],
                recursive=True,
            )
            by_rel = dict(entries)
            self.assertEqual(by_rel["f.txt"](), b"bytes")
            self.assertEqual(by_rel["t.txt"](), b"text")
            self.assertEqual(by_rel["p.bin"](), b"\x01\x02")


class uploadfolder__FakeFile:
    def __init__(self, name: str) -> None:
        self.name = name

    def after_execute(self, fn):
        return self


class TestUploadFolderChain(unittest.TestCase):
    def test_chain_uploads_in_order_with_progress(self):
        folder = uploadfolder__folder()
        callbacks = []  # (relative_path, after_execute_fn) as the chain registers them
        seen_progress = []
        uploaded_files = []

        def _fake_upload(rel, content, chunk_size=4 * 1024 * 1024):
            fake = uploadfolder__FakeFile(rel)
            orig = fake.after_execute

            def _capture(fn):
                callbacks.append((rel, fn))
                return orig(fn)

            fake.after_execute = _capture
            return fake

        with mock.patch.object(folder, "upload_file", side_effect=_fake_upload):
            result = MoveCopyUtil.upload_folder(
                folder,
                [("a.txt", b"a"), ("docs/b.txt", b"b")],
                after_file_uploaded=lambda f: uploaded_files.append(f.name),
                progress=lambda p: seen_progress.append(p.done),
            )
            self.assertEqual(result, folder)
            self.assertEqual(len(callbacks), 1)  # first upload queued, chain not driven

            while callbacks:  # drive the deferred chain FIFO
                _rel, fn = callbacks.pop(0)
                fn(uploadfolder__FakeFile(_rel))

        self.assertEqual(seen_progress, [1, 2])  # noqa: PLR2004
        self.assertEqual(uploaded_files, ["a.txt", "docs/b.txt"])


def zipfolder__folder() -> Folder:
    ctx = ClientContext("https://contoso.sharepoint.com/sites/x")
    return ctx.web.root_folder


def _zip_stream() -> io.BytesIO:
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("docs/a.txt", "alpha")
        zf.writestr("b.csv", "1,2")
        zf.writestr("empty/", "")  # directory entry — must be skipped
    buffer.seek(0)
    return buffer


class zipfolder__FakeFile:
    def __init__(self, name: str) -> None:
        self.name = name

    def after_execute(self, fn):
        return self


class TestUploadFolderFromZip(unittest.TestCase):
    def test_uploads_literal_entries_in_order(self):
        folder = zipfolder__folder()
        callbacks = []
        seen_progress = []
        uploaded = []

        def _fake_upload(rel, content, chunk_size=4 * 1024 * 1024):
            fake = zipfolder__FakeFile(rel)
            orig = fake.after_execute

            def _capture(fn):
                callbacks.append((rel, fn))
                return orig(fn)

            fake.after_execute = _capture
            return fake

        with mock.patch.object(folder, "upload_file", side_effect=_fake_upload):
            result = MoveCopyUtil.upload_folder_from_zip(
                folder,
                _zip_stream(),
                after_file_uploaded=lambda f: uploaded.append(f.name),
                progress=lambda p: seen_progress.append(p.done),
            )
            self.assertEqual(result, folder)
            self.assertEqual(len(callbacks), 1)  # first entry queued; chain not driven

            while callbacks:  # drive the deferred chain FIFO
                rel, fn = callbacks.pop(0)
                fn(zipfolder__FakeFile(rel))

        # literal paths in order; directory entries skipped
        self.assertEqual(uploaded, ["b.csv", "docs/a.txt"])
        self.assertEqual(seen_progress, [1, 2])  # noqa: PLR2004
