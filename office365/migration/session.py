"""Migration session — the SPMT-shaped facade over a batch of migrations.

Mirrors the ``Microsoft.SharePoint.MigrationTool.PowerShell`` cmdlets:

| cmdlet | method |
|---|---|
| ``Register-SPMTMigration`` | :meth:`MigrationSession.register` |
| ``Get-SPMTMigration`` | :meth:`MigrationSession.get` |
| ``Add-SPMTTask`` | :meth:`MigrationSession.add_task` |
| ``Remove-SPMTTask`` | :meth:`MigrationSession.remove_task` |
| ``Show-SPMTMigration`` | :meth:`MigrationSession.show` |
| ``Start-SPMTMigration`` | :meth:`MigrationSession.start` |
| ``Stop-SPMTMigration`` | :meth:`MigrationSession.stop` |
| ``Unregister-SPMTMigration`` | :meth:`MigrationSession.unregister` |

A task pairs a source and a target adapter — either supplied directly, or
declared as a :class:`~office365.migration.tasks.MigrationTask` (resolved against
the registered ``ClientContext``).
"""

from __future__ import annotations

import itertools
import logging
import re
import threading
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import TYPE_CHECKING

from office365.migration.base import MigrationOptions, MigrationPhase
from office365.migration.job import MigrationJob
from office365.migration.logging import log_event

if TYPE_CHECKING:
    from office365.migration.delta import DeltaReport
    from office365.migration.settings import MigrationSettings
    from office365.migration.tasks import MigrationTask
    from office365.migration.throttling import ThrottleMonitor

__all__ = ["MigrationSession", "SessionTask"]

#: Job phases a session does not run again (a resume re-plans only unfinished work).
_TERMINAL_PHASES = frozenset(
    {
        MigrationPhase.COMPLETED,
        MigrationPhase.COMPLETED_WITH_ERRORS,
        MigrationPhase.CANCELLED,
    }
)


def _display_label(target) -> str:
    """A short, human label for a target adapter (``list:Documents`` -> ``Documents``).

    Progress lines name the object being copied, and a server-relative URL or an
    adapter prefix is noise there; the last path segment is what an operator calls
    the library.
    """
    label = getattr(target, "label", None)
    text = str(label()) if callable(label) else type(target).__name__
    kind, _, value = text.partition(":")
    if not value:
        return kind
    leaf = value.rstrip("/").rsplit("/", 1)[-1]
    return leaf or kind or text


def _site_list_slug(target) -> str:
    """A filesystem-safe slug for a resolved target adapter (``library:<url>``)."""
    label = getattr(target, "label", None)
    text = str(label()) if callable(label) else type(target).__name__
    text = text.split(":", 1)[-1]
    slug = re.sub(r"[^A-Za-z0-9._-]+", "-", text).strip("-")
    return slug or "list"


def _child_path(directory, label: str, name: str):
    """``<directory>/<label>.<name>`` (or ``None`` when no directory is set)."""
    if directory is None:
        return None
    from pathlib import Path

    return Path(directory) / f"{label}.{name}"


def _throttle_fields(monitor: "ThrottleMonitor | None") -> dict:
    """The throttling counters to add to a run event — nothing without a monitor."""
    return monitor.snapshot() if monitor is not None else {}


def _job_status(job: MigrationJob) -> dict:
    """Project a job's state — the status form of a session task."""
    return {
        "source": job.source_label,
        "target": job.target_label,
        "phase": job.phase.value,
        "duration_ms": job.duration_ms,
        "fidelity": job.fidelity().summary(),
        "stats": {
            "total": job.stats.total,
            "success": job.stats.success,
            "skipped": job.stats.skipped,
            "errors": job.stats.errors,
            "bytes_transferred": job.stats.bytes_transferred,
        },
    }


@dataclass
class SessionTask:
    """A registered task: an id, its descriptor (when declared), and its job."""

    id: str
    job: MigrationJob
    descriptor: "MigrationTask | None" = None

    def status(self) -> dict:
        data = _job_status(self.job)
        data["id"] = self.id
        if self.descriptor is not None:
            data["descriptor"] = self.descriptor.label()
        return data


class MigrationSession:
    """A batch of migration tasks, driven like the SPMT PowerShell cmdlets."""

    def __init__(
        self,
        options: MigrationOptions | None = None,
        context=None,
        settings=None,
        throttle: "ThrottleMonitor | None" = None,
    ) -> None:
        self._options = options
        self._context = context
        self._settings = settings
        self._throttle = throttle
        self._tasks: list[SessionTask] = []
        self._ids = itertools.count(1)
        self._warnings: list[str] = []
        self._settings_noted = False

    @property
    def throttle(self) -> "ThrottleMonitor | None":
        """The throttling monitor this session reports, if one was supplied."""
        return self._throttle

    # ── Cmdlets ──────────────────────────────────────────────────

    def register(self, settings: "MigrationSettings | None" = None, context=None) -> "MigrationSession":
        """Register the session — its settings and the target ``ClientContext``."""
        if settings is not None:
            self._settings = settings
        if context is not None:
            self._context = context
        return self

    def get(self) -> "MigrationSession":
        """The registered session (``Get-SPMTMigration``)."""
        return self

    def add_task(
        self,
        source=None,
        target=None,
        *,
        task: "MigrationTask | None" = None,
        options: MigrationOptions | None = None,
        provision_structure: bool = True,
        manifest_path=None,
        checkpoint_path=None,
        **descriptor,
    ) -> MigrationJob:
        """Add a task — adapters directly, a ``MigrationTask``, or task kwargs.

        Descriptor kwargs (``file_share_source`` / ``target_site_url`` /
        ``target_list`` …) are resolved against the registered context. A resolved
        SharePoint task replays the source list's structure onto the target list
        before content is copied; pass ``provision_structure=False`` to skip that.
        """
        if task is None and descriptor:
            from office365.migration.tasks import MigrationTask

            task = MigrationTask(**descriptor)
        self._note_unhonored_settings()
        if task is not None:
            if task.migrate_all:
                raise ValueError("use add_site_task() for a whole-site (migrate_all) task")
            if self._context is None:
                raise ValueError("register a ClientContext first (session.register(context=ctx))")
            from office365.migration.sharepoint.resolvers import resolve_task

            source, target = resolve_task(task, self._context, self._settings, provision_structure=provision_structure)
        job = MigrationJob(
            source,
            target,
            self._effective_options(options),
            manifest_path=manifest_path,
            checkpoint_path=checkpoint_path,
        )
        self._tasks.append(SessionTask(str(next(self._ids)), job, task))
        return job

    def add_site_task(
        self,
        *,
        task: "MigrationTask | None" = None,
        options: MigrationOptions | None = None,
        include=None,
        exclude=None,
        provision_structure: bool = True,
        include_subwebs: bool = False,
        manifest_dir=None,
        checkpoint_dir=None,
        progress=None,
        **descriptor,
    ) -> list[MigrationJob]:
        """Add a whole-site (``migrate_all``) task — one job per source list/library.

        Returns the jobs created, in source order. Each job gets its own manifest
        and checkpoint; pass ``manifest_dir`` / ``checkpoint_dir`` to persist them
        as ``<index>-<list>.manifest.json`` / ``<index>-<list>.checkpoint.json`` so
        a large site resumes per list instead of restarting. With
        ``provision_structure`` (the default), each target list's columns, content
        types and views are replayed from the source before content is copied.

        Subsites are detected but skipped unless ``include_subwebs`` is set; a note
        naming them is surfaced through :meth:`warnings` when they are skipped. Each
        web's modern site pages are copied unless ``settings.migrate_pages`` is
        false; classic pages and web part data bindings are reported instead. Each
        web's ``Title``/``Description`` are copied onto the target when they differ
        (``settings.migrate_site_settings``, ``NONE`` to leave the target web alone);
        branding and the site-collection/regional settings are reported, not
        carried.

        ``progress`` is a ``ProgressCallback`` fired while the plan is resolved —
        target containers created, each list's structure replayed — which is
        otherwise the quiet phase between the inventory and the first copy.
        """
        if task is None and descriptor:
            from office365.migration.tasks import MigrationTask

            task = MigrationTask(**descriptor)
        if task is None:
            raise ValueError("a site task is required")
        if self._context is None:
            raise ValueError("register a ClientContext first (session.register(context=ctx))")
        from office365.migration.sharepoint.resolvers import resolve_site_task
        from office365.migration.sharepoint.site_settings import parse_site_settings_mode

        self._note_unhonored_settings()
        effective = self._effective_options(options)
        pairs = resolve_site_task(
            task,
            self._context,
            self._settings,
            include=include,
            exclude=exclude,
            provision_structure=provision_structure,
            include_subwebs=include_subwebs,
            preserve_permissions=bool(effective and effective.preserve_permissions),
            migrate_navigation=bool(self._settings and self._settings.migrate_navigation),
            migrate_pages=self._settings.migrate_pages if self._settings is not None else True,
            duplicate_page_behavior=(self._settings.duplicate_page_behavior if self._settings is not None else "RENAME"),
            migrate_site_settings=parse_site_settings_mode(
                self._settings.migrate_site_settings if self._settings is not None else None
            ),
            warnings=self._warnings,
            progress=progress,
        )
        jobs: list[MigrationJob] = []
        for index, (source, target) in enumerate(pairs, start=1):
            label = f"{index:02d}-{_site_list_slug(target)}"
            job = MigrationJob(
                source,
                target,
                self._effective_options(options),
                manifest_path=_child_path(manifest_dir, label, "manifest.json"),
                checkpoint_path=_child_path(checkpoint_dir, label, "checkpoint.json"),
            )
            self._tasks.append(SessionTask(str(next(self._ids)), job, task))
            jobs.append(job)
        return jobs

    def remove_task(self, task) -> None:
        """Remove a task by its ``MigrationJob``, ``SessionTask`` or id."""
        for entry in list(self._tasks):
            if task in (entry, entry.job, entry.id):
                self._tasks.remove(entry)
                return
        raise KeyError(task)

    def show(self) -> list[dict]:
        """The per-task status (``Show-SPMTMigration``)."""
        return [entry.status() for entry in self._tasks]

    def start(self, progress=None, concurrency: int = 1) -> list[dict]:
        """Start the migration: plan + run every registered task.

        ``progress`` is the ``ProgressCallback`` handed to each job (and on to the
        runner), so one :class:`~office365.migration.logging.ProgressReporter` can
        heartbeat the whole session.

        ``concurrency`` is how many tasks run **at once** (default ``1``: one after
        another). Because a whole-site task resolves to one job per list, this is
        the site-level knob: a site of many small lists is waiting on round trips,
        not on bandwidth, and copies them in parallel. Each job gets its own
        context clone (:meth:`~office365.migration.job.MigrationJob.rebind`), so
        threads never share a pending-query queue while still sharing the
        authenticated transport — and therefore the same connection pool, retry
        policy and rate limiter. A shared
        :class:`~office365.migration.logging.ProgressReporter` is derived per job so
        heartbeats keep their own counters and label.
        """
        statuses: list[dict | None] = [None] * len(self._tasks)
        started = datetime.now(timezone.utc)
        log_event("run.started", tasks=len(self._tasks))
        throttled = self._throttle.throttled if self._throttle is not None else 0
        try:
            if concurrency > 1:
                self._run_parallel(progress, concurrency, statuses)
            else:
                for index, entry in enumerate(self._tasks):
                    reporter = self._reporter(progress, entry)
                    statuses[index] = self._run_entry(entry, reporter, isolated=False)
                    throttled = self._note_throttling(throttled)
        finally:
            done = [status for status in statuses if status is not None]
            totals = {"success": 0, "skipped": 0, "errors": 0}
            for status in done:
                for key in totals:
                    totals[key] += status.get("stats", {}).get(key) or 0
            log_event(
                "run.completed",
                f"{len(done)} task(s): {totals['success']} copied, "
                f"{totals['skipped']} skipped, {totals['errors']} failed",
                duration_ms=int((datetime.now(timezone.utc) - started).total_seconds() * 1000),
                tasks=len(done),
                **totals,
                **_throttle_fields(self._throttle),
            )
        return [status for status in statuses if status is not None]

    def _run_entry(self, entry: "SessionTask", progress, *, isolated: bool) -> dict:
        """Plan and run one task, optionally on context-isolated adapters."""
        job = entry.job
        if job.phase in _TERMINAL_PHASES:
            return entry.status()
        if isolated:
            # Adopt the copy *before* running: if the run fails part-way, the
            # session still reports what it copied instead of a job that never moved.
            job = job.rebind()
            entry.job = job
        try:
            job.plan(progress)
            job.run(progress)
        finally:
            # Emit the last heartbeat so the final count is never lost (and a
            # caller watching the stream sees this list finish).
            close = getattr(progress, "close", None)
            if callable(close):
                close()
        return entry.status()

    def _run_parallel(self, progress, concurrency: int, statuses: list[dict | None]) -> None:
        """Run the registered jobs on a thread pool (one cloned context per job)."""
        from concurrent.futures import ThreadPoolExecutor, as_completed

        workers = max(1, min(concurrency, len(self._tasks)))
        log_event("run.parallel", tasks=len(self._tasks), concurrency=workers)
        lock = threading.Lock()
        throttled = self._throttle.throttled if self._throttle is not None else 0

        def _work(index: int, entry: "SessionTask") -> None:
            status = self._run_entry(entry, self._reporter(progress, entry), isolated=True)
            with lock:
                statuses[index] = status

        with ThreadPoolExecutor(max_workers=workers, thread_name_prefix="migration") as pool:
            futures = [pool.submit(_work, index, entry) for index, entry in enumerate(self._tasks)]
            for future in as_completed(futures):
                future.result()  # a task failure stops the session, as it does sequentially
                throttled = self._note_throttling(throttled)

    def _reporter(self, progress, entry: "SessionTask"):
        """A per-job view of ``progress``: own counters, the list's name for a label.

        Derived in both modes: a single reporter sharing one set of counters would
        carry a rate and a container total from the previous list into the next one.
        """
        if hasattr(progress, "derive"):
            return progress.derive(_display_label(entry.job.target))
        return progress

    def _note_throttling(self, seen: int) -> int:
        """Emit a ``throttled`` event when the monitor counted more since ``seen``.

        The event carries the cumulative counters (``responses``, ``throttled``,
        ``retry_after_s``, ``by_status``) so a collector can chart a run's
        throttling over time rather than only its total.
        """
        if self._throttle is None:
            return seen
        snapshot = self._throttle.snapshot()
        if snapshot["throttled"] > seen:
            log_event("throttled", self._throttle.summary(), level=logging.WARNING, **snapshot)
        return snapshot["throttled"]

    def stop(self) -> None:
        """Cancel the session (``Stop-SPMTMigration``); tasks stay resumable."""
        for entry in self._tasks:
            entry.job.cancel()

    def pause(self) -> None:
        """Request a clean stop at the next batch boundary (resumable)."""
        for entry in self._tasks:
            entry.job.pause()

    def unregister(self) -> None:
        """Drop all tasks and release the session (``Unregister-SPMTMigration``)."""
        self._tasks.clear()
        self._warnings.clear()

    # ── State ────────────────────────────────────────────────────

    @property
    def tasks(self) -> list[SessionTask]:
        return self._tasks

    @property
    def jobs(self) -> list[MigrationJob]:
        return [entry.job for entry in self._tasks]

    def status(self) -> list[dict]:
        """The per-task status (alias of :meth:`show`)."""
        return self.show()

    def verify(self, spot_checks: int = 20):
        """Reconcile source vs target for every task after migration."""
        return [entry.job.verify(spot_checks) for entry in self._tasks]

    def warnings(self) -> list[str]:
        """Adapter warnings accumulated by the tasks (anything not migrated faithfully).

        Adapters may expose a ``warnings`` list; messages collected there (for
        example an attachment skipped for lack of a file name, or a target column
        that could not be created) are surfaced here so a run never silently drops
        data. Resolution-level notes (for example subsites skipped by a whole-site
        task) are included too.
        """
        messages: list[str] = list(self._warnings)
        for entry in self._tasks:
            for adapter in (entry.job.source, entry.job.target):
                messages.extend(getattr(adapter, "warnings", None) or [])
        return messages

    def fidelity(self) -> list[dict]:
        """Per-task fidelity report — what each run will (and won't) preserve.

        Empty before any task is added. Each entry is a JSON-serializable dict
        (see :class:`~office365.migration.fidelity.FidelityReport`).
        """
        return [entry.job.fidelity().to_dict() for entry in self._tasks]

    def delta(self) -> list["DeltaReport"]:
        """Per-task drift against the plan the previous run persisted.

        One entry per task, in registration order. A task whose plan has no
        baseline (a first run, or no ``manifest_dir``/``manifest_path``) reports
        an empty delta; nothing is deleted on the target, so drift is named for
        an operator to act on.
        """
        return [entry.job.delta for entry in self._tasks]

    # ── Helpers ──────────────────────────────────────────────────

    def _note_unhonored_settings(self) -> None:
        """Surface the settings that ask for behavior the engine does not implement.

        ``MigrationSettings`` mirrors the SPMT cmdlet surface, which is wider than
        what a client-side run can do (``skip_lists_with_name``, term groups,
        multi-round, custom Azure storage …). Reporting them once per session keeps
        a run from reading as honoring a knob it ignores.
        """
        if self._settings_noted or self._settings is None:
            return
        self._settings_noted = True
        self._warnings.extend(self._settings.unhonored())

    def _effective_options(self, options: MigrationOptions | None) -> MigrationOptions | None:
        """Resolve the options for a new job: explicit > session > settings.

        Registering ``MigrationSettings`` (the SPMT surface) now feeds its fidelity
        flags into each task by default; an explicit ``options`` argument, or
        options passed to :meth:`__init__`, still win.
        """
        if options is not None:
            return options
        if self._options is not None:
            return self._options
        if self._settings is not None:
            return self._settings.to_options()
        return None
