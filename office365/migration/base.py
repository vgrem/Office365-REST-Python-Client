"""
Shared types and enums for the migration toolkit.
"""

from __future__ import annotations

import re
from dataclasses import asdict, dataclass, field, fields
from enum import Enum

from office365.runtime.limits import DEFAULT_BATCH_SIZE
from office365.runtime.operations import OperationStats


class ConflictResolution(str, Enum):
    SKIP = "skip"
    OVERWRITE = "overwrite"
    RENAME = "rename"


def conflict_to_on_conflict(conflict: ConflictResolution) -> str:
    """Map a migration conflict policy to a record pipeline ``on_conflict`` value.

    ``OVERWRITE`` reconciles an existing keyed record (``"update"``); ``SKIP`` is
    create-if-missing (``"skip"``). ``RENAME`` has no record-level meaning — a
    record is keyed, not pathed — so it also maps to ``"skip"``.
    """
    return "update" if conflict == ConflictResolution.OVERWRITE else "skip"


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
    source_id: str | None = None  # source item identity (e.g. file UniqueId), for the old→new map
    version_label: str | None = None  # current version label (e.g. ``"3.0"``)
    # Older versions, oldest first, as ``(label, content)`` — populated only for a
    # target that preserves version history (server-side package). Transient: NOT
    # persisted in the checkpoint (keyed by ``dest_path``), so no blobs on disk.
    versions: list[tuple[str, bytes]] | None = None
    # Resolved authorship identities (server-side package path only). Persisted in
    # the manifest (they are small, JSON-safe dicts), never checkpointed.
    author: "Principal | None" = None
    editor: "Principal | None" = None


# SharePoint Online renders ``UserInfo.UserId.NameId`` as a 16-character hex PUID
# (e.g. ``100320006514b083``). A GUID (dashed), a claims login, or the app
# principal's id must be rejected: emitting one makes the Migration API ingestion
# job fail to deserialize the user map (``System.FormatException`` — the service
# schema's documented behaviour; this rejection was not re-probed on the lab
# tenant, whose own user map ingests fine).
_PUID_PATTERN = re.compile(r"^[0-9a-fA-F]{16}$")
#: Not part of the PUID: some clients render the value as a ``0x``-prefixed
#: literal, and a value read from a payload may carry surrounding whitespace.
_PUID_PREFIXES = ("0x", "0X")


def normalize_puid(value: "str | None") -> "str | None":
    """The PUID carried by ``value`` (its 16 hex digits), or ``None``.

    The digits are what ``UserGroup.xml``'s ``SystemId`` carries, so a ``0x``
    prefix and surrounding whitespace are stripped here rather than written into
    the attribute: the service parses the value as a number, not as a Python-style
    literal. The digits' case is preserved (the service reads them as hex either
    way, and a needless rewrite would obscure a surprising source value).
    """
    if not value:
        return None
    text = str(value).strip()
    for prefix in _PUID_PREFIXES:
        if text.startswith(prefix):
            text = text[len(prefix) :]
            break
    return text if _PUID_PATTERN.match(text) else None


def is_puid(value: "str | None") -> bool:
    """Whether ``value`` is a usable SharePoint PUID (``UserInfo.UserId.NameId``).

    The Migration API's ``UserGroup.xml`` ``SystemId`` carries the user's PUID,
    which SharePoint Online exposes as a 16-character hex string (the digits may
    include ``a``-``f``). A GUID, a claims login, or the app principal's id makes
    the ingestion job fail to deserialize the user map, so such principals are
    treated as unresolved and skipped (best-effort).
    """
    return normalize_puid(value) is not None


@dataclass
class Principal:
    """A resolved user identity, used for authorship and ACL fidelity.

    ``system_id`` is the user's PUID (``UserInfo.UserId.NameId``) — the value the
    Migration API's ``UserGroup.xml`` ``SystemId`` requires, in its canonical
    form (see :func:`normalize_puid`). A GUID or a claims login there fails the
    ingestion job, so only a resolved PUID is carried.
    """

    login_name: str
    system_id: str | None = None
    display_name: str | None = None
    email: str | None = None


@dataclass
class PermissionEntry:
    """A single principal → role-names grant, used for best-effort ACL preservation.

    Produced by :meth:`DataSource.read_permissions` and consumed by
    :meth:`DataTarget.apply_permissions`; role names are the target's role
    definition names (e.g. ``"Read"``, ``"Edit"``, ``"Full Control"``).

    The optional identity fields (``system_id``/``display_name``/``email``) and
    ``role_masks`` let the server-side package target emit a faithful
    ``UserGroup.xml``/``DeploymentRoles`` payload; the client-side REST path and
    the permission diff ignore them.
    """

    principal_name: str
    roles: list[str] = field(default_factory=list)
    # PUID (``UserInfo.UserId.NameId``) for a user principal; ``None`` for a group
    # or an unresolved principal (the package target skips those).
    system_id: str | None = None
    display_name: str | None = None
    email: str | None = None
    # Role name -> decimal permission mask (e.g. ``"Read" -> "756052856929"``).
    role_masks: dict[str, str] = field(default_factory=dict)


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
    # Fidelity flags. ``preserve_timestamps``, ``preserve_authorship`` and
    # ``preserve_permissions`` are applied client-side on a best-effort basis when
    # the adapters support it (see ``DataSource.read_permissions`` /
    # ``DataTarget.apply_timestamps`` / ``DataTarget.apply_authorship`` /
    # ``DataTarget.apply_permissions``); REST cannot restore version history, so
    # ``preserve_versions`` requires the server-side Migration API
    # (``MigrationServerJob``). Defaults are False so they are honest no-ops
    # rather than silently doing nothing.
    preserve_timestamps: bool = False
    preserve_permissions: bool = False
    preserve_authorship: bool = False
    preserve_versions: bool = False
    include_patterns: list[str] = field(default_factory=list)
    exclude_patterns: list[str] = field(default_factory=list)
    # Date window (ISO-8601): skip items created/modified at or before these
    created_after: str | None = None
    modified_after: str | None = None
    batch_size: int = DEFAULT_BATCH_SIZE
    concurrency: int = 1  # parallel workers for bulk file upload / batched writes


def item_to_dict(item: MigrationItem) -> dict:
    """Serialize a ``MigrationItem`` to a JSON-safe dict (enum/error by value).

    ``versions`` (transient version blobs, read only during a run) is dropped — it
    is not JSON-serializable and lives on the in-flight item only.
    """
    data = asdict(item)
    data.pop("versions", None)
    data["status"] = item.status.value
    data["error"] = str(item.error) if item.error else None
    return data


def item_from_dict(data: dict) -> MigrationItem:
    """Rebuild a ``MigrationItem`` (missing fields fall back to dataclass defaults)."""
    kwargs = {f.name: data[f.name] for f in fields(MigrationItem) if f.name in data}
    if "status" in kwargs:
        kwargs["status"] = ItemStatus(kwargs["status"])
    for principal_field in ("author", "editor"):
        value = kwargs.get(principal_field)
        if isinstance(value, dict):
            kwargs[principal_field] = Principal(**value)
    return MigrationItem(**kwargs)
