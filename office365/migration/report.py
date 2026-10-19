"""Migration reports — summary, item, and failure exports.

Builds records from the job's existing state (:class:`MigrationStats`, the
manifest's per-item status, and the checkpoint) and exports them as CSV and JSON
through the records interchange — the same neutral form the data pipeline uses
for collections.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING

from office365.migration.report_io import write_formats
from office365.runtime.converters.scalars import iso

if TYPE_CHECKING:
    from office365.migration.job import MigrationJob


@dataclass
class MigrationReport:
    """Record sets for a migration run (one summary row, per-item rows)."""

    summary: list[dict[str, object]] = field(default_factory=list)
    items: list[dict[str, object]] = field(default_factory=list)
    failures: list[dict[str, object]] = field(default_factory=list)


def _gb(value: int) -> float:
    """Bytes -> gigabytes, rounded to two decimals."""
    return round(value / (1024**3), 2)


def _extension(path: str) -> str:
    """File/folder extension (SPMT leaves folders with an empty extension)."""
    _, dot, ext = path.rpartition(".")
    return ext if dot else ""


def _identity_fields(job: "MigrationJob") -> dict[str, object]:
    """Identity-map counters for the summary row (empty when no map is configured)."""
    identity_map = job.options.identity_map
    return identity_map.summary() if identity_map is not None else {}


def build_report(job: "MigrationJob") -> MigrationReport:
    """Project a job's state into report records."""
    stats = job.stats
    total_bytes = sum(i.size_bytes for i in job.manifest.items)
    migrated_gb = _gb(stats.bytes_transferred)
    duration_secs = job.duration
    gb_per_hour = round(migrated_gb / (duration_secs / 3600), 2) if duration_secs else None
    summary = [
        {
            "source": job.source_label,
            "destination": job.target_label,
            "status": job.phase.value,
            "total_bytes": total_bytes,
            "total_gb": _gb(total_bytes),
            "total_items": stats.total,
            "success": stats.success,
            "skipped": stats.skipped,
            "errors": stats.errors,
            "items_not_migrated": stats.skipped + stats.errors,
            "bytes_transferred": stats.bytes_transferred,
            "migrated_gb": migrated_gb,
            "not_migrated_gb": _gb(total_bytes - stats.bytes_transferred),
            "warnings": 0,
            "gb_per_hour": gb_per_hour,
            "run_id": job.checkpoint.run_id,
            "started_at": iso(job.started_at),
            "finished_at": iso(job.finished_at),
            "duration_secs": round(duration_secs, 1) if duration_secs is not None else None,
            **_identity_fields(job),
        }
    ]
    items = [
        {
            "source_path": item.source_path,
            "destination_path": item.dest_path,
            "file_name": item.dest_path.rsplit("/", 1)[-1],
            "extension": _extension(item.dest_path),
            "size_bytes": item.size_bytes,
            "item_type": item.item_type,
            "status": item.status.value,
            "error": item.error or "",
            "error_code": item.error_code or "",
            "modified": item.modified or "",
            "created": item.created or "",
            "author_id": item.author_id,
            "editor_id": item.editor_id,
        }
        for item in job.manifest.items
    ]
    failures = [row for row in items if row["status"] == "failed"]
    return MigrationReport(summary=summary, items=items, failures=failures)


def export_reports(job: "MigrationJob", output_dir: str | Path) -> list[str]:
    """Write SummaryReport, ItemReport, and FailureReport (CSV + JSON).

    The failure report is only written when failures exist.

    Args:
        job: The migration job to report on.
        output_dir: Directory to write the report files into.

    Returns:
        List of written file paths.
    """
    report = build_report(job)
    written: list[str] = []
    for name, records in (
        ("SummaryReport", report.summary),
        ("ItemReport", report.items),
        ("FailureReport", report.failures),
    ):
        if not records:
            continue
        written += write_formats(records, output_dir, name)
    return written
