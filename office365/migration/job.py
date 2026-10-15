"""Migration job — a single client-side copy between source and target.

Lifecycle: ``assess -> plan -> run -> verify``, with pause/resume
from a persisted checkpoint. The job is platform-agnostic — it works against any
``DataSource`` / ``DataTarget`` adapter pair. (For server-side Azure ingestion,
see :class:`MigrationServerJob` instead.)
"""

from __future__ import annotations

import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import TYPE_CHECKING, Any, Callable, cast

from office365.migration.base import MigrationOptions, MigrationPhase, MigrationStats
from office365.migration.checkpoint import Checkpoint
from office365.migration.manifest import Manifest
from office365.migration.runner import MigrationRunner

if TYPE_CHECKING:
    from office365.runtime.operations import Progress


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
        """Enumerate the source into a persisted manifest."""
        self._checkpoint.phase = MigrationPhase.PLANNING
        self._manifest = Manifest.from_source(self._source, progress)
        self._save_state()
        return self._manifest

    def run(self, progress: Callable[["Progress"], None] | None = None) -> MigrationStats:
        """Execute the migration (resumable; re-drives pending/failed items)."""
        self._checkpoint.phase = MigrationPhase.RUNNING
        self._started_at = datetime.now(timezone.utc)
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
        self._finished_at = datetime.now(timezone.utc)
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
        :meth:`run`. The run itself still fails fast on an unhonorable flag.
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

    def _load_state(self) -> None:
        if self._manifest_path is not None and Path(self._manifest_path).exists():
            self._manifest = Manifest.load(self._manifest_path)
        if self._checkpoint_path is not None and Path(self._checkpoint_path).exists():
            self._checkpoint = Checkpoint.load(self._checkpoint_path)
