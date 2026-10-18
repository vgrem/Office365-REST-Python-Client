"""Migration toolkit — resumable, client-side migrations.

The core is product-agnostic: it composes a ``DataSource``/``DataTarget`` pair
(filesystem, SharePoint, ...) with checkpoints, resumption, and verification.
Product packages add the platform-specific pieces:
``office365.migration.sharepoint`` and ``office365.migration.outlook``.

Quick start (filesystem -> filesystem):

    from office365.migration import MigrationJob
    from office365.migration.adapters.filesystem import FileSystemSource, FileSystemTarget

    job = MigrationJob(FileSystemSource("src"), FileSystemTarget("dst"))
    job.plan()
    job.run()
    print(job.stats.summary())
    print(job.verify().summary())

Product conveniences (``MigrationAssessor``, ``MailboxAssessor``, ...) are
re-exported lazily, so importing the core never pulls in SharePoint or Outlook.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from office365.migration.assessment.containers import ScanContainer
from office365.migration.assessment.registry import ScanDefinition, scan_pairs
from office365.migration.assessment.report import AssessmentReport, ScanReport
from office365.migration.assessment.scanners import AssessmentOptions
from office365.migration.base import (
    ConflictResolution,
    ExportFormat,
    ItemStatus,
    MigrationItem,
    MigrationOptions,
    MigrationPhase,
    MigrationStats,
    conflict_to_on_conflict,
)
from office365.migration.checkpoint import Checkpoint
from office365.migration.delta import DeltaReport, MovedItem, compute_delta
from office365.migration.fidelity import FidelityReport, FidelityStatus, describe_fidelity
from office365.migration.job import MigrationJob
from office365.migration.logging import (
    JsonLogFormatter,
    ProgressReporter,
    configure_json_logging,
    log_event,
)
from office365.migration.manifest import Manifest
from office365.migration.map import ContentTypeMap
from office365.migration.report import MigrationReport, build_report, export_reports
from office365.migration.runner import MigrationRunner
from office365.migration.server_job import MigrationServerJob
from office365.migration.session import MigrationSession, SessionTask
from office365.migration.settings import MigrationSettings
from office365.migration.tasks import MigrationTask
from office365.migration.throttling import ThrottleMonitor
from office365.migration.validators import VerificationReport, verify

if TYPE_CHECKING:
    # Product conveniences resolved lazily by ``__getattr__`` (declared here so
    # type checkers and ``__all__`` see them without importing the products).
    from office365.migration.outlook import OUTLOOK_SCANS, MailboxAssessor, OutlookOptions
    from office365.migration.sharepoint import (
        SHAREPOINT_SCANS,
        MigrationAssessor,
        MigrationTenantAssessor,
    )
    from office365.migration.teams import (
        TeamsArchiveSource,
        TeamsArchiveTarget,
        TeamsExportOptions,
    )

_LAZY_EXPORTS = {
    "MigrationAssessor": "office365.migration.sharepoint",
    "MigrationTenantAssessor": "office365.migration.sharepoint",
    "SHAREPOINT_SCANS": "office365.migration.sharepoint",
    "MailboxAssessor": "office365.migration.outlook",
    "OutlookOptions": "office365.migration.outlook",
    "OUTLOOK_SCANS": "office365.migration.outlook",
    "TeamsArchiveSource": "office365.migration.teams",
    "TeamsArchiveTarget": "office365.migration.teams",
    "TeamsExportOptions": "office365.migration.teams",
}

__all__ = [
    "AssessmentOptions",
    "AssessmentReport",
    "Checkpoint",
    "ConflictResolution",
    "ContentTypeMap",
    "DeltaReport",
    "ExportFormat",
    "FidelityReport",
    "ItemStatus",
    "JsonLogFormatter",
    "Manifest",
    "MigrationItem",
    "MigrationJob",
    "MigrationOptions",
    "MigrationPhase",
    "MigrationReport",
    "MigrationRunner",
    "MigrationServerJob",
    "MigrationSession",
    "MigrationSettings",
    "MigrationStats",
    "MigrationTask",
    "ProgressReporter",
    "MovedItem",
    "ScanContainer",
    "ScanDefinition",
    "ScanReport",
    "SessionTask",
    "ThrottleMonitor",
    "VerificationReport",
    "build_report",
    "compute_delta",
    "configure_json_logging",
    "conflict_to_on_conflict",
    "describe_fidelity",
    "log_event",
    "FidelityStatus",
    "export_reports",
    "scan_pairs",
    "verify",
    "MigrationAssessor",
    "MigrationTenantAssessor",
    "SHAREPOINT_SCANS",
    "MailboxAssessor",
    "OutlookOptions",
    "OUTLOOK_SCANS",
    "TeamsArchiveSource",
    "TeamsArchiveTarget",
    "TeamsExportOptions",
]


def __getattr__(name: str):
    """Resolve product conveniences lazily (keeps the core import light)."""
    module_name = _LAZY_EXPORTS.get(name)
    if module_name is None:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    import importlib

    return getattr(importlib.import_module(module_name), name)
