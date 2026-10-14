"""Post-migration verification — reconcile source against target.

The validator is layered, and honest about what it can and cannot confirm:

1. **Presence** — expected items missing on the target, and unexpected items
   present there (``missing`` / ``extra``); always runs.
2. **Content** — a checksum spot-check sample (``spot_checks``); skipped entries
   whose adapters expose no comparable checksum are reported as ``unverifiable``.
3. **Fidelity** — when the run requested ``preserve_timestamps`` /
   ``preserve_permissions``, the same sample is diffed via the optional
   ``read_metadata(item)`` / ``read_permissions(item)`` adapter hooks. If an
   adapter does not expose the hook the check is reported as ``unverifiable``,
   never silently skipped. ``preserve_versions`` cannot be verified over REST and
   is always reported as ``unverifiable``.

A requested check that could not be run therefore shows up in
``VerificationReport.unverifiable`` and makes ``complete`` false while leaving
``ok`` true when no actual discrepancy was found.
"""

from __future__ import annotations

import random
from typing import Any

from office365.migration.adapters import DataSource, DataTarget
from office365.migration.base import MigrationItem, MigrationOptions, PermissionEntry
from office365.migration.manifest import Manifest
from office365.runtime.converters.scalars import parse_datetime
from office365.runtime.verification import VerificationReport

__all__ = ["VerificationReport", "verify"]

_METADATA_KEYS = ("created", "modified")


def verify(
    source: DataSource,
    target: DataTarget,
    manifest: Manifest,
    spot_checks: int = 20,
    options: MigrationOptions | None = None,
) -> VerificationReport:
    """Reconcile the source against the target, including requested fidelity.

    Args:
        source: Source adapter.
        target: Target adapter.
        manifest: The migration plan (expected destination paths).
        spot_checks: Number of items sampled for the content/metadata/ACL checks.
        options: The run's options; when given, its ``preserve_*`` flags decide
            which fidelity checks run (otherwise only presence + content are
            checked).
    """
    expected = {item.dest_path for item in manifest.items}
    target_paths = set(target.list_paths())
    report = VerificationReport(source_count=len(expected), target_count=len(target_paths))

    for path in sorted(expected - target_paths):
        report.missing.append(path)
    for path in sorted(target_paths - expected):
        report.extra.append(path)

    candidates = [item for item in manifest.items if item.dest_path in target_paths and item.item_type != "folder"]
    sample = random.sample(candidates, min(spot_checks, len(candidates)))

    _verify_content(source, target, sample, report)
    if options is not None:
        if options.preserve_timestamps:
            _verify_metadata(source, target, sample, report)
        if options.preserve_permissions:
            _verify_permissions(source, target, sample, report)
        if options.preserve_versions:
            report.unverifiable.append(
                "versions: REST cannot verify version history (needs the server-side Migration API)"
            )
    return report


def _verify_content(source: DataSource, target: DataTarget, items: list[MigrationItem], report) -> None:
    for item in items:
        try:
            source_sum = source.checksum(item)
            target_sum = target.checksum(item)
        except Exception as e:  # noqa: BLE001 — an unreadable item is a caveat, not a crash
            report.unverifiable.append(f"content: {item.dest_path} ({e})")
            continue
        if not source_sum or not target_sum:
            # e.g. a record target does not expose a comparable content hash
            report.unverifiable.append(f"content: {item.dest_path} (no checksum)")
            continue
        report.checked += 1
        if source_sum != target_sum:
            report.mismatches.append(f"content mismatch: {item.dest_path}")


def _verify_metadata(source, target, items: list[MigrationItem], report) -> None:
    source_read = getattr(source, "read_metadata", None)
    target_read = getattr(target, "read_metadata", None)
    if not (callable(source_read) and callable(target_read)):
        report.unverifiable.append("timestamps: adapters do not implement read_metadata(item)")
        return
    for item in items:
        try:
            source_meta: Any = source_read(item)
            target_meta: Any = target_read(item)
        except Exception as e:  # noqa: BLE001
            report.unverifiable.append(f"timestamps: {item.dest_path} ({e})")
            continue
        if not source_meta or not target_meta:
            report.unverifiable.append(f"timestamps: {item.dest_path} (no metadata)")
            continue
        for key in _METADATA_KEYS:
            if key in source_meta and key in target_meta and not _same_time(source_meta[key], target_meta[key]):
                report.mismatches.append(f"timestamp mismatch ({key}): {item.dest_path}")


def _verify_permissions(source, target, items: list[MigrationItem], report) -> None:
    source_read = getattr(source, "read_permissions", None)
    target_read = getattr(target, "read_permissions", None)
    if not (callable(source_read) and callable(target_read)):
        report.unverifiable.append("permissions: adapters do not both implement read_permissions(item)")
        return
    for item in items:
        try:
            source_perms: Any = source_read(item) or []
            target_perms: Any = target_read(item) or []
        except Exception as e:  # noqa: BLE001
            report.unverifiable.append(f"permissions: {item.dest_path} ({e})")
            continue
        if _permission_set(source_perms) != _permission_set(target_perms):
            report.mismatches.append(f"permission mismatch: {item.dest_path}")


def _permission_set(entries: list[PermissionEntry]) -> set[tuple[str, frozenset[str]]]:
    return {(entry.principal_name, frozenset(entry.roles)) for entry in entries}


def _same_time(a: Any, b: Any) -> bool:
    """Whether two timestamps denote the same instant (tolerant of tz formatting)."""
    if a is None or b is None:
        return a == b
    left, right = parse_datetime(a), parse_datetime(b)
    if left is not None and right is not None:
        return left == right
    return str(a) == str(b)
