"""Post-migration verification — reconcile source against target.

The validator is layered, and honest about what it can and cannot confirm:

1. **Presence** — expected items missing on the target, and unexpected items
   present there (``missing`` / ``extra``); always runs.
2. **Content** — a checksum spot-check sample (``spot_checks``); skipped entries
   whose adapters expose no comparable checksum are reported as ``unverifiable``.
   Office Open XML documents that md5-differ are compared canonically (ignoring the
   ``docProps/`` / ``customXml/`` / ``[trash]/`` parts SharePoint rewrites on
   upload), so document property promotion is a caveat rather than a false mismatch.
3. **Fidelity** — when the run requested ``preserve_timestamps`` /
   ``preserve_authorship`` / ``preserve_permissions``, the same sample is diffed
   via the optional ``read_metadata(item)`` / ``read_authorship(item)`` /
   ``read_permissions(item)`` adapter hooks. List-item attachments are
   content-only (their system metadata has no client-settable backing), so they
   are excluded from these diffs and reported once as ``unverifiable``. If an
   adapter does not expose the hook the check is reported as ``unverifiable``,
   never silently skipped. ``preserve_versions`` cannot be verified over REST and
   is always reported as ``unverifiable``.

A requested check that could not be run therefore shows up in
``VerificationReport.unverifiable`` and makes ``complete`` false while leaving
``ok`` true when no actual discrepancy was found.
"""

from __future__ import annotations

import io
import random
import zipfile
from typing import Any

from office365.migration.adapters import DataSource, DataTarget
from office365.migration.base import MigrationItem, MigrationOptions, PermissionEntry
from office365.migration.manifest import Manifest
from office365.runtime.converters.scalars import parse_datetime
from office365.runtime.verification import VerificationReport

__all__ = ["VerificationReport", "verify"]

_METADATA_KEYS = ("created", "modified")

#: Office Open XML documents SharePoint may re-serialize on upload.
_OFFICE_OPEN_XML_EXTENSIONS = (
    ".docx",
    ".docm",
    ".dotx",
    ".dotm",
    ".xlsx",
    ".xlsm",
    ".xltx",
    ".xltm",
    ".pptx",
    ".pptm",
    ".potx",
    ".potm",
)

#: Package parts SharePoint owns during document property promotion/demotion.
_SERVER_OWNED_OFFICE_PARTS = ("docProps/", "customXml/", "[trash]/")


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
    folder_candidates = [
        item for item in manifest.items if item.dest_path in target_paths and item.item_type == "folder"
    ]
    folder_sample: list[MigrationItem] = []
    if folder_candidates:
        # A folder's column values are content too: a document set's metadata is part
        # of what was migrated, not an attribute of the container. Only adapters that
        # carry and can compare them are checked, so the filesystem pair stays silent.
        if getattr(source, "supports_folder_records", False) and getattr(target, "supports_folder_records", False):
            folder_sample = random.sample(folder_candidates, min(spot_checks, len(folder_candidates)))
            _verify_content(source, target, folder_sample, report)
    if options is not None:
        wants_fidelity = (
            options.preserve_timestamps
            or options.preserve_authorship
            or options.preserve_permissions
            or options.preserve_versions
        )
        # Attachments are content-only: SharePoint exposes no client-side path to
        # set an attachment's own system metadata (it has no backing list item),
        # so the fidelity diffs run on records/files and the gap is stated once.
        fidelity_sample = [item for item in sample if item.item_type != "attachment"] if wants_fidelity else sample
        if wants_fidelity and len(fidelity_sample) < len(sample):
            report.unverifiable.append(
                f"attachments: {len(sample) - len(fidelity_sample)} sampled attachment(s) are "
                "content-only (their system metadata cannot be set over REST)"
            )
        if wants_fidelity:
            # A folder is an item too: the timestamps/authorship/ACL writes land on
            # its list item, so the same diffs run over the folder sample — only for
            # the pairs that carry folder records, which are the ones that report
            # folder fidelity at all.
            fidelity_sample.extend(folder_sample)
        if options.preserve_timestamps:
            _verify_metadata(source, target, fidelity_sample, report)
        if options.preserve_authorship:
            _verify_authorship(source, target, fidelity_sample, report)
        if options.preserve_permissions:
            _verify_permissions(source, target, fidelity_sample, report)
        if options.preserve_versions:
            report.unverifiable.append(
                "versions: REST cannot verify version history (needs the server-side Migration API)"
            )
    return report


def _canonical_office_parts(data: Any) -> dict[str, bytes] | None:
    """The Office Open XML package parts SharePoint does not own, or ``None``.

    Returns ``None`` when ``data`` is not a readable zip archive (so a corrupt or
    non-Office payload never compares equal by accident).
    """
    if not isinstance(data, (bytes, bytearray)):
        return None
    try:
        with zipfile.ZipFile(io.BytesIO(data)) as archive:
            return {
                name: archive.read(name)
                for name in archive.namelist()
                if not name.startswith(_SERVER_OWNED_OFFICE_PARTS)
            }
    except Exception:  # noqa: BLE001 — not an Office Open XML package
        return None


def _office_content_equivalent(source: Any, target: Any, item: MigrationItem) -> bool:
    """Whether two Office documents are equivalent apart from server-owned parts.

    SharePoint re-serializes Office Open XML documents on upload (document
    property promotion/demotion rewrites ``docProps/``, ``customXml/`` and
    ``[trash]/``), so a raw md5 of a client-side REST round-trip is not stable.
    Compare the remaining package parts exactly instead; a difference there is a
    real mismatch.
    """
    source_read = getattr(source, "read", None)
    target_read = getattr(target, "read", None)
    if not (callable(source_read) and callable(target_read)):
        return False
    if not item.dest_path.lower().endswith(_OFFICE_OPEN_XML_EXTENSIONS):
        return False
    try:
        source_parts = _canonical_office_parts(source_read(item))
        target_parts = _canonical_office_parts(target_read(item))
    except Exception:  # noqa: BLE001 — an unreadable side is simply "not equivalent"
        return False
    return source_parts is not None and target_parts is not None and source_parts == target_parts


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
        if source_sum == target_sum:
            continue
        if _office_content_equivalent(source, target, item):
            report.unverifiable.append(
                f"content: {item.dest_path} (Office document re-serialized by SharePoint property promotion)"
            )
            continue
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
        expected_status = source_meta.get("moderation_status")
        if expected_status is not None:
            actual_status = target_meta.get("moderation_status")
            if actual_status is None:
                report.unverifiable.append(f"approval state: {item.dest_path} (target reports none)")
            elif expected_status != actual_status:
                report.mismatches.append(f"approval state mismatch: {item.dest_path}")


def _verify_authorship(source, target, items: list[MigrationItem], report) -> None:
    source_read = getattr(source, "read_authorship", None)
    target_read = getattr(target, "read_authorship", None)
    if not (callable(source_read) and callable(target_read)):
        report.unverifiable.append("authorship: adapters do not implement read_authorship(item)")
        return
    for item in items:
        try:
            source_authors: Any = source_read(item)
            target_authors: Any = target_read(item)
        except Exception as e:  # noqa: BLE001
            report.unverifiable.append(f"authorship: {item.dest_path} ({e})")
            continue
        if source_authors != target_authors:
            report.mismatches.append(f"authorship mismatch: {item.dest_path}")


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
        if left.tzinfo is None and right.tzinfo is not None:
            left = left.replace(tzinfo=right.tzinfo)
        elif right.tzinfo is None and left.tzinfo is not None:
            right = right.replace(tzinfo=left.tzinfo)
        return left == right
    return str(a) == str(b)
