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
import re
from dataclasses import dataclass
from typing import TYPE_CHECKING

from office365.migration.base import MigrationOptions, MigrationPhase
from office365.migration.job import MigrationJob

if TYPE_CHECKING:
    from office365.migration.delta import DeltaReport
    from office365.migration.settings import MigrationSettings
    from office365.migration.tasks import MigrationTask

__all__ = ["MigrationSession", "SessionTask"]


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


def _job_status(job: MigrationJob) -> dict:
    """Project a job's state — the status form of a session task."""
    return {
        "source": job.source_label,
        "target": job.target_label,
        "phase": job.phase.value,
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

    def __init__(self, options: MigrationOptions | None = None, context=None, settings=None) -> None:
        self._options = options
        self._context = context
        self._settings = settings
        self._tasks: list[SessionTask] = []
        self._ids = itertools.count(1)
        self._warnings: list[str] = []

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
        false; classic pages and web part data bindings are reported instead.
        """
        if task is None and descriptor:
            from office365.migration.tasks import MigrationTask

            task = MigrationTask(**descriptor)
        if task is None:
            raise ValueError("a site task is required")
        if self._context is None:
            raise ValueError("register a ClientContext first (session.register(context=ctx))")
        from office365.migration.sharepoint.resolvers import resolve_site_task

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
            warnings=self._warnings,
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

    def start(self, progress=None) -> list[dict]:
        """Start the migration: plan + run every registered task."""
        statuses: list[dict] = []
        for entry in self._tasks:
            job = entry.job
            if job.phase in (
                MigrationPhase.COMPLETED,
                MigrationPhase.COMPLETED_WITH_ERRORS,
                MigrationPhase.CANCELLED,
            ):
                statuses.append(entry.status())
                continue
            job.plan(progress)
            job.run(progress)
            statuses.append(entry.status())
        return statuses

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
