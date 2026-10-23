"""Offline tests for running a site's lists concurrently.

A whole-site task resolves to one job per list, so for a site of many small lists
the run is a queue of small jobs — and the serial queue, not the per-item copy, is
what makes it slow. ``MigrationSession.start(concurrency=...)`` overlaps those jobs
without changing what the target receives: each worker gets its own context clone
(one pending-query queue per job) that still shares the authenticated transport and
the rate limiter.

Also covers the other half of the same phase: resolution (container creation and
per-list structure replay) reports through the same ``Progress`` heartbeat the
runner emits, instead of being the quiet stretch between the plan and the copy.
"""

from __future__ import annotations

import threading

from office365.migration import MigrationTask
from office365.migration.adapters.filesystem import FileSystemSource, FileSystemTarget
from office365.migration.base import MigrationPhase
from office365.migration.job import MigrationJob
from office365.migration.logging import ProgressReporter
from office365.migration.session import MigrationSession
from office365.migration.sharepoint import resolvers
from office365.migration.sharepoint.adapters import (
    SharePointLibrarySource,
    SharePointLibraryTarget,
)
from office365.sharepoint.client_context import ClientContext
from tests._scripted_transport import RoutingTransport

SITE_URL = "https://contoso.sharepoint.com/sites/target"
SOURCE_URL = "https://contoso.sharepoint.com/sites/source"
LIST_ID = "0f3e4c1a-9b2d-4a6f-8c11-2b7e5d9a4c33"
LIST_ROUTE = "lists"
FOLDER_ROUTE = "getFolderByServerRelativePath"
DIGEST_ROUTE = "contextInfo"
FILES_PER_JOB = 2
JOBS = 4
BARRIER_TIMEOUT = 10.0
CLONE_CONCURRENCY = 3


# ── Fixtures ─────────────────────────────────────────────────────


def _seed(root) -> None:
    """Two files in a folder — enough for a real plan/run cycle."""
    (root / "docs").mkdir(parents=True)
    (root / "docs" / "a.txt").write_text("alpha")
    (root / "b.txt").write_text("beta")


class _GatedSource(FileSystemSource):
    """Waits until every worker is in flight — the pool's ordering probe.

    A sequential session would block on the barrier until it breaks, so this
    doubles as a regression test for "concurrency was silently ignored".
    """

    def __init__(self, root, gate: threading.Barrier) -> None:
        super().__init__(root)
        self._gate = gate

    def list_items(self, progress=None):
        self._gate.wait(timeout=BARRIER_TIMEOUT)
        return super().list_items(progress)


class _LabelledTarget(FileSystemTarget):
    """A target labelled the way a SharePoint adapter labels one."""

    def label(self) -> str:
        return "library:/sites/target/Documents"


def _session_with_jobs(tmp_path, count: int, make_source) -> MigrationSession:
    """A session of ``count`` filesystem jobs, each in its own directory pair."""
    session = MigrationSession()
    for index in range(count):
        source = tmp_path / f"src{index}"
        _seed(source)
        session.add_task(make_source(source), FileSystemTarget(tmp_path / f"dst{index}"))
    return session


def _context(routes: list[tuple[str, object]]) -> ClientContext:
    """A target context whose requests are answered from ``routes``."""
    ctx = ClientContext(SITE_URL)
    ctx.with_access_token(_token)  # offline: the transport never sees the network
    ctx.pending_request().transport = RoutingTransport([(DIGEST_ROUTE, _digest_payload()), *routes])
    return ctx


def _token() -> dict:
    return {"access_token": "token", "token_type": "Bearer", "expiresIn": 3600}


def _digest_payload() -> dict:
    """Every write needs a form digest; a clone fetches its own, once."""
    return {
        "d": {
            "GetContextWebInformation": {
                "FormDigestValue": "0x0123456789",
                "FormDigestTimeoutSeconds": 1800,
                "LibraryVersion": "16.0.0.0",
                "WebFullUrl": SITE_URL,
            }
        }
    }


def _list_payload(title: str = "Documents") -> dict:
    return {"d": {"Id": LIST_ID, "Title": title, "BaseTemplate": 101}}


# ── The session pool ─────────────────────────────────────────────


def test_jobs_run_at_the_same_time(tmp_path):
    gate = threading.Barrier(JOBS)
    session = _session_with_jobs(tmp_path, JOBS, lambda source: _GatedSource(source, gate))

    statuses = session.start(concurrency=JOBS)

    assert len(statuses) == JOBS
    assert [status["phase"] for status in statuses] == [MigrationPhase.COMPLETED.value] * JOBS
    assert [status["stats"]["success"] for status in statuses] == [FILES_PER_JOB] * JOBS
    for index in range(JOBS):
        assert (tmp_path / f"dst{index}" / "docs" / "a.txt").read_text() == "alpha"
    # Four threads, but the statuses come back in registration order.
    assert [status["id"] for status in statuses] == [str(index) for index in range(1, JOBS + 1)]
    assert [status["id"] for status in session.show()] == [status["id"] for status in statuses]


def test_a_serial_run_names_each_list_in_its_progress(tmp_path):
    # A shared reporter would carry one list's rate and total into the next; every
    # job gets its own counters, labelled with the list's name rather than its URL.
    session = MigrationSession()
    _seed(tmp_path / "src")
    session.add_task(FileSystemSource(tmp_path / "src"), _LabelledTarget(tmp_path / "dst"))
    beats: list = []

    session.start(progress=ProgressReporter(interval=0, emit=beats.append))

    assert {beat["label"] for beat in beats} == {"Documents"}
    assert beats[-1]["done"] == beats[-1]["total"]


# ── Rebinding: one pending-query queue per job ──────────────────


class _Rebindable:
    """A stand-in adapter that records how often it was re-addressed."""

    def __init__(self) -> None:
        self.rebound = 0

    def rebind(self) -> "_Rebindable":
        copy = _Rebindable()
        copy.rebound = self.rebound + 1
        return copy

    def label(self) -> str:
        return "fake"


def test_rebind_copies_a_context_bound_job_and_keeps_its_state_paths():
    job = MigrationJob(
        _Rebindable(),
        _Rebindable(),
        manifest_path="m.json",
        checkpoint_path="c.json",
    )

    copy = job.rebind()

    assert copy is not job
    assert copy.source is not job.source
    assert copy.source.rebound == 1
    assert copy._manifest_path == job._manifest_path
    assert copy._checkpoint_path == job._checkpoint_path
    assert job.source.rebound == 0  # the original was left untouched


def test_library_target_rebinds_folder_and_list_on_one_clone():
    folder_payload = {"d": {"Exists": True, "Name": "Documents", "ServerRelativeUrl": "/sites/target/Documents"}}
    ctx = _context([(LIST_ROUTE, _list_payload()), (FOLDER_ROUTE, folder_payload)])
    folder = ctx.web.get_folder_by_server_relative_path("/sites/target/Documents").get().execute_query()
    sp_list = ctx.web.lists.get_by_id(LIST_ID).get().execute_query()
    target = SharePointLibraryTarget(folder, concurrency=CLONE_CONCURRENCY, sp_list=sp_list)

    rebound = target.rebind()

    assert rebound._folder.context is not ctx
    assert rebound._concurrency == CLONE_CONCURRENCY
    # One clone for the whole rebind: folder and list share it, so their queries
    # queue and execute together instead of racing each other on the original.
    assert rebound._sp_list.context is rebound._folder.context
    assert rebound._folder.context.pending_request().transport is ctx.pending_request().transport


def test_library_source_rebinds_folder_and_list_on_one_clone():
    folder_payload = {"d": {"Exists": True, "Name": "Documents", "ServerRelativeUrl": "/sites/target/Documents"}}
    ctx = _context([(LIST_ROUTE, _list_payload()), (FOLDER_ROUTE, folder_payload)])
    folder = ctx.web.get_folder_by_server_relative_path("/sites/target/Documents").get().execute_query()
    sp_list = ctx.web.lists.get_by_id(LIST_ID).get().execute_query()
    source = SharePointLibrarySource(folder, sp_list=sp_list)

    rebound = source.rebind()

    assert rebound._folder.context is not ctx
    assert rebound._sp_list.context is rebound._folder.context
    assert rebound.label() == source.label()


# ── Resolution progress ─────────────────────────────────────────


def test_site_resolution_forwards_the_progress_callback(monkeypatch):
    captured = {}

    def _fake_resolve_web(*args, **kwargs):
        captured.update(kwargs)

    monkeypatch.setattr(resolvers, "_resolve_web", _fake_resolve_web)
    monkeypatch.setattr(resolvers, "_context_for", lambda ctx, url: ctx)

    seen: list = []
    task = MigrationTask.sharepoint(SOURCE_URL, SITE_URL, migrate_all=True)

    pairs = resolvers.resolve_site_task(task, object(), None, progress=seen.append)

    assert pairs == []
    assert captured["progress"] == seen.append
