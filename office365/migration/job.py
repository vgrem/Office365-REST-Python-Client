"""Migration job — a single client-side copy between source and target.

Lifecycle: ``assess -> plan -> run -> verify``, with pause/resume
from a persisted checkpoint. The job is platform-agnostic — it works against any
``DataSource`` / ``DataTarget`` adapter pair. (For server-side Azure ingestion,
see :class:`MigrationServerJob` instead.)
"""

from __future__ import annotations

import logging
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import TYPE_CHECKING, Any, Callable, cast

from office365.migration.base import MigrationItem, MigrationOptions, MigrationPhase, MigrationStats
from office365.migration.checkpoint import Checkpoint
from office365.migration.delta import DeltaReport, compute_delta
from office365.migration.logging import log_event
from office365.migration.manifest import Manifest
from office365.migration.runner import MigrationRunner

if TYPE_CHECKING:
    from office365.runtime.operations import Progress


def _elapsed_ms(started: datetime, finished: datetime | None = None) -> int:
    """Whole milliseconds between two UTC timestamps (for the event payload)."""
    end = finished or datetime.now(timezone.utc)
    return int((end - started).total_seconds() * 1000)


def _rebind_adapter(adapter):
    """The adapter re-addressed on its own context, or the adapter itself.

    Adapters opt in by exposing ``rebind()`` (the SharePoint ones do); the ones that
    hold no runtime context (filesystem, in-memory) are shared as they are.
    """
    rebind = getattr(adapter, "rebind", None)
    return rebind() if callable(rebind) else adapter


class MigrationJob:
    """A resumable migration between a source and a target adapter."""

    def __init__(
        self,
        source,
        target,
        options: MigrationOptions | None = None,
        run_id: str | None = None,
        manifest_path: str | Path | None = None,
        checkpoint_path: str | Path | None = None,
    ) -> None:
        self._source = source
        self._target = target
        self._options = options or MigrationOptions()
        self._manifest = Manifest()
        self._delta = DeltaReport()
        self._checkpoint = Checkpoint.create(run_id)
        self._stats = MigrationStats()
        self._manifest_path = manifest_path
        self._checkpoint_path = checkpoint_path
        self._runner = MigrationRunner()
        self._stop_event = threading.Event()
        self._cancel_requested = False
        self._assess_hook: Any = None
        self._started_at: datetime | None = None
        self._finished_at: datetime | None = None

    # ── Configuration ────────────────────────────────────────────

    def with_assessor(self, hook) -> "MigrationJob":
        """Attach a pre-flight assessment (a ``MigrationAssessor`` or a callable).

        The hook runs during :meth:`assess` and is the "scan" phase of the job.
        """
        self._assess_hook = hook
        return self

    def rebind(self) -> "MigrationJob":
        """This job with context-isolated adapters — a copy safe to run on a thread.

        A job's adapters may hold a ``ClientRuntimeContext`` (the SharePoint adapters
        do), and a context owns a single pending-query queue: two jobs sharing one
        cannot run at the same time. Adapters that expose ``rebind()`` are
        re-addressed on a ``clone`` (which shares the authenticated transport, so the
        whole fleet still uses one connection pool); the rest are context-free and
        shared. Returns ``self`` when nothing had to change, so a sequential run is
        untouched.

        The copy starts from a fresh phase and stats — it is meant to be created
        *before* the job runs, which is what a session does before handing it to a
        worker thread.
        """
        source = _rebind_adapter(self._source)
        target = _rebind_adapter(self._target)
        if source is self._source and target is self._target:
            return self
        return MigrationJob(
            source,
            target,
            self._options,
            manifest_path=self._manifest_path,
            checkpoint_path=self._checkpoint_path,
        )

    # ── State ────────────────────────────────────────────────────

    @property
    def phase(self) -> MigrationPhase:
        return self._checkpoint.phase

    @property
    def stats(self) -> MigrationStats:
        return self._stats

    @property
    def options(self) -> MigrationOptions:
        """The effective options for this job (defaults when none were supplied)."""
        return self._options

    @property
    def manifest(self) -> Manifest:
        return self._manifest

    @property
    def delta(self) -> DeltaReport:
        """What changed at the source since the persisted plan (a re-run's drift).

        Filled by :meth:`plan` when ``manifest_path`` holds the plan a previous
        run wrote: deleted, renamed/moved and changed items are named there so a
        copy that cannot converge on them says so instead of passing silently.
        """
        return self._delta

    @property
    def checkpoint(self) -> Checkpoint:
        return self._checkpoint

    @property
    def source(self):
        """The source adapter for this job."""
        return self._source

    @property
    def target(self):
        """The target adapter for this job."""
        return self._target

    @property
    def source_label(self) -> str:
        """A human-readable label for the source (adapter type / root)."""
        label = getattr(self._source, "label", None)
        return str(label()) if callable(label) else type(self._source).__name__

    @property
    def target_label(self) -> str:
        label = getattr(self._target, "label", None)
        return str(label()) if callable(label) else type(self._target).__name__

    @property
    def started_at(self) -> datetime | None:
        return self._started_at

    @property
    def finished_at(self) -> datetime | None:
        return self._finished_at

    @property
    def duration(self) -> float | None:
        """Wall-clock duration of the last run, in seconds."""
        if self._started_at is None or self._finished_at is None:
            return None
        return (self._finished_at - self._started_at).total_seconds()

    @property
    def duration_ms(self) -> int | None:
        """Wall-clock duration of the last run, in milliseconds (log payloads)."""
        duration = self.duration
        return None if duration is None else int(duration * 1000)

    # ── Lifecycle ────────────────────────────────────────────────

    def assess(self, progress: Callable[["Progress"], None] | None = None) -> object | None:
        """Run the pre-migration assessment (the "scan" phase).

        Accepts a ``MigrationAssessor`` or a callable attached via
        :meth:`with_assessor`; ``progress`` is forwarded when the hook is a
        ``MigrationAssessor``.
        """
        self._checkpoint.phase = MigrationPhase.ASSESSING
        self._save_state()
        hook = self._assess_hook
        assess: Any = getattr(hook, "assess", None)
        if callable(assess):
            result = cast(Any, assess(progress=progress))
            return result.execute_query().value
        if callable(hook):
            return hook()
        return None

    def plan(self, progress: Callable[["Progress"], None] | None = None) -> Manifest:
        """Enumerate the source into a persisted manifest.

        When the manifest path already holds a plan, that plan is the baseline of
        a delta comparison (:attr:`delta`) before it is replaced.
        """
        self._checkpoint.phase = MigrationPhase.PLANNING
        started = datetime.now(timezone.utc)
        # No labels here: a SharePoint source has not read its list yet, so its
        # server-relative URL is still unknown — ``plan.completed`` carries both.
        log_event("plan.started")
        previous, note = self._previous_plan()
        self._manifest = Manifest.from_source(self._source, progress)
        self._delta = compute_delta(previous, self._manifest.items, note=note)
        self._save_state()
        log_event(
            "plan.completed",
            f"{self.source_label}: {len(self._manifest.items)} item(s) planned",
            source=self.source_label,
            target=self.target_label,
            items=len(self._manifest.items),
            duration_ms=_elapsed_ms(started),
        )
        return self._manifest

    def run(self, progress: Callable[["Progress"], None] | None = None) -> MigrationStats:
        """Execute the migration (resumable; re-drives pending/failed items)."""
        self._checkpoint.phase = MigrationPhase.RUNNING
        self._started_at = datetime.now(timezone.utc)
        log_event(
            "job.started",
            f"{self.source_label} -> {self.target_label}",
            source=self.source_label,
            target=self.target_label,
            items=len(self._manifest.items),
        )
        try:
            self._stats = self._runner.run(
                self._source,
                self._target,
                self._manifest.items,
                self._options,
                self._checkpoint,
                self._checkpoint_path,
                progress,
                stop_event=self._stop_event.is_set,
            )
        except Exception as e:
            self._finished_at = datetime.now(timezone.utc)
            log_event(
                "job.failed",
                f"{self.source_label} -> {self.target_label} failed: {e}",
                level=logging.ERROR,
                source=self.source_label,
                target=self.target_label,
                error=str(e),
                duration_ms=self.duration_ms,
            )
            raise
        self._finished_at = datetime.now(timezone.utc)
        log_event(
            "job.completed",
            f"{self.target_label}: {self._stats.success} copied, {self._stats.skipped} skipped"
            f", {self._stats.errors} failed",
            source=self.source_label,
            target=self.target_label,
            phase=self._checkpoint.phase.value,
            success=self._stats.success,
            skipped=self._stats.skipped,
            errors=self._stats.errors,
            bytes_transferred=self._stats.bytes_transferred,
            duration_ms=self.duration_ms,
        )
        if self._checkpoint.phase == MigrationPhase.PAUSED and self._cancel_requested:
            self._checkpoint.phase = MigrationPhase.CANCELLED
            self._save_state()
        return self._stats

    def pause(self) -> None:
        """Request a clean stop at the next batch boundary (checkpoint saved)."""
        self._stop_event.set()

    def cancel(self) -> None:
        """Request cancellation; the job is marked ``cancelled`` and stays resumable."""
        self._cancel_requested = True
        self._stop_event.set()

    def resume(self, progress: Callable[["Progress"], None] | None = None) -> MigrationStats:
        """Reload persisted state (if any) and continue from the last checkpoint."""
        self._load_state()
        self._stop_event.clear()
        self._cancel_requested = False
        return self.run(progress)

    def status(self) -> MigrationPhase:
        return self.phase

    def fidelity(self):
        """Describe the requested fidelity this job's adapter pair can honor.

        Purely informational (never raises); use it to report capabilities before
        :meth:`run`. The run itself still fails fast on an unhonorable flag. The
        report also carries the full per-dimension fidelity matrix
        (``report.dimensions`` / ``report.matrix_summary()``).
        """
        from office365.migration.fidelity import describe_fidelity

        return describe_fidelity(self._source, self._target, self._options)

    def verify(self, spot_checks: int = 20):
        """Reconcile source vs target after migration.

        Always checks presence and content checksums; when the run requested
        fidelity flags, the same sample is diffed for timestamps/permissions via
        the optional adapter ``read_metadata`` / ``read_permissions`` hooks (see
        :func:`office365.migration.validators.verify`).
        """
        from office365.migration.validators import verify as _verify

        self._checkpoint.phase = MigrationPhase.VERIFYING
        report = _verify(self._source, self._target, self._manifest, spot_checks, self._options)
        self._checkpoint.phase = MigrationPhase.COMPLETED if report.ok else MigrationPhase.COMPLETED_WITH_ERRORS
        return report

    def export_reports(self, output_dir: str | Path):
        """Write Summary/Item/Failure reports (CSV + JSON) for the last run.

        Reuses the migration state (stats, manifest, checkpoint) through the
        records form — see :mod:`office365.migration.report`.

        Args:
            output_dir: Directory to write the report files into.

        Returns:
            List of written file paths.
        """
        from office365.migration.report import export_reports as _export_reports

        return _export_reports(self, output_dir)

    # ── Helpers ──────────────────────────────────────────────────

    def _save_state(self) -> None:
        if self._manifest_path is not None:
            self._manifest.save(self._manifest_path)
        if self._checkpoint_path is not None:
            self._checkpoint.save(self._checkpoint_path)

    def _previous_plan(self) -> tuple[list[MigrationItem] | None, str | None]:
        """The plan a previous run persisted (the delta baseline), if there is one."""
        if self._manifest_path is None:
            return None, None
        path = Path(self._manifest_path)
        if not path.exists():
            return None, None
        try:
            return Manifest.load(path).items, None
        except Exception as e:  # noqa: BLE001 — a broken baseline must not block a re-plan
            return None, f"the previous plan at {path} could not be read ({e})"

    def _load_state(self) -> None:
        if self._manifest_path is not None and Path(self._manifest_path).exists():
            self._manifest = Manifest.load(self._manifest_path)
        if self._checkpoint_path is not None and Path(self._checkpoint_path).exists():
            self._checkpoint = Checkpoint.load(self._checkpoint_path)
