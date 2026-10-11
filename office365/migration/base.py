"""
Shared types and enums for the migration toolkit.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field, fields
from enum import Enum

from office365.runtime.limits import DEFAULT_BATCH_SIZE
from office365.runtime.operations import OperationStats


class ConflictResolution(str, Enum):
    SKIP = "skip"
    OVERWRITE = "overwrite"
    RENAME = "rename"


class MigrationMode(str, Enum):
    FULL = "full"
    INCREMENTAL = "incremental"
    UPSERT = "upsert"

    inProgress = "0"

    completed = "1"

    unknownFutureValue = "2"

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.MigrationMode"


class ExportFormat(str, Enum):
    FILESYSTEM = "filesystem"
    PARQUET = "parquet"
    CSV = "csv"
    JSON = "json"
    DELTA = "delta"


class ItemStatus(str, Enum):
    """Per-item status, persisted in the checkpoint for resumable migrations."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    DONE = "done"
    SKIPPED = "skipped"
    FAILED = "failed"


class MigrationPhase(str, Enum):
    """Lifecycle of a migration job (scan -> plan -> run -> monitor).

    ``paused`` / ``failed`` / ``cancelled`` all retain a persisted checkpoint, so
    the job can be resumed from where it stopped.
    """

    CREATED = "created"
    ASSESSING = "assessing"
    PLANNING = "planning"
    RUNNING = "running"
    PAUSED = "paused"
    VERIFYING = "verifying"
    COMPLETED = "completed"
    COMPLETED_WITH_ERRORS = "completed_with_errors"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class MigrationItem:
    """Unit of work flowing through the migration pipeline."""

    source_path: str
    dest_path: str
    size_bytes: int = 0
    item_type: str = "file"
    status: ItemStatus = ItemStatus.PENDING
    error: str | None = None  # failure message (SPMT "Message")
    error_code: str | None = None  # failure category/code (e.g. exception type name)
    modified: str | None = None  # source last-modified (ISO-8601), for incremental
    created: str | None = None  # source created (ISO-8601)
    author_id: int | None = None  # source author user id (system ``AuthorId``)
    editor_id: int | None = None  # source last-modified-by user id (system ``EditorId``)


@dataclass
class PermissionEntry:
    """A single principal → role-names grant, used for best-effort ACL preservation.

    Produced by :meth:`DataSource.read_permissions` and consumed by
    :meth:`DataTarget.apply_permissions`; role names are the target's role
    definition names (e.g. ``"Read"``, ``"Edit"``, ``"Full Control"``).
    """

    principal_name: str
    roles: list[str] = field(default_factory=list)


@dataclass
class MigrationStats(OperationStats):
    bytes_transferred: int = 0

    def summary(self) -> str:
        mb = self.bytes_transferred / 1024 / 1024
        return (
            f"Total: {self.total} | Success: {self.success} | "
            f"Skipped: {self.skipped} | Errors: {self.errors} | "
            f"Transferred: {mb:.1f}MB"
        )


@dataclass
class MigrationOptions:
    conflict_resolution: ConflictResolution = ConflictResolution.SKIP
    incremental: bool = False  # skip items at/below the persisted watermark (and target-newer ones)
    # Fidelity flags. ``preserve_timestamps`` and ``preserve_permissions`` are
    # applied client-side on a best-effort basis when the adapters support it
    # (see ``DataSource.read_permissions`` / ``DataTarget.apply_timestamps`` /
    # ``DataTarget.apply_permissions``); REST cannot restore version history, so
    # ``preserve_versions`` requires the server-side Migration API
    # (``MigrationServerJob``). Defaults are False so they are honest no-ops
    # rather than silently doing nothing.
    preserve_timestamps: bool = False
    preserve_permissions: bool = False
    preserve_versions: bool = False
    include_patterns: list[str] = field(default_factory=list)
    exclude_patterns: list[str] = field(default_factory=list)
    # Date window (ISO-8601): skip items created/modified at or before these
    created_after: str | None = None
    modified_after: str | None = None
    batch_size: int = DEFAULT_BATCH_SIZE
    concurrency: int = 1  # parallel workers for bulk file upload / batched writes


def item_to_dict(item: MigrationItem) -> dict:
    """Serialize a ``MigrationItem`` to a JSON-safe dict (enum/error by value)."""
    data = asdict(item)
    data["status"] = item.status.value
    data["error"] = str(item.error) if item.error else None
    return data


def item_from_dict(data: dict) -> MigrationItem:
    """Rebuild a ``MigrationItem`` (missing fields fall back to dataclass defaults)."""
    kwargs = {f.name: data[f.name] for f in fields(MigrationItem) if f.name in data}
    if "status" in kwargs:
        kwargs["status"] = ItemStatus(kwargs["status"])
    return MigrationItem(**kwargs)
