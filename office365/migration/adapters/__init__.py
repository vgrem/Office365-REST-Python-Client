"""Source/target adapters for the migration runner.

A migration moves items from a :class:`DataSource` to a :class:`DataTarget`
through a canonical form (bytes for files, dict records for tabular data).
Adapters implement this small contract, so the runner is platform-agnostic —
SharePoint, the filesystem, and (later) S3 / PostgreSQL / Kafka all plug in here.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Iterable
from typing import TYPE_CHECKING, Callable, Optional

from office365.migration.base import ConflictResolution, MigrationItem

if TYPE_CHECKING:
    from office365.runtime.operations import Progress

# NOTE: runtime-evaluated alias, so keep Optional (the ``|`` operator is 3.10+).
MigrationProgress = Optional[Callable[["Progress"], None]]


class DataSource(ABC):
    """Reads migration items from a source.

    Optional hooks (not declared here so ``hasattr`` reflects real support):

    - ``read_permissions(item) -> list[PermissionEntry]`` — the item's ACLs, used
      for best-effort ``preserve_permissions`` and for the permission diff;
    - ``read_metadata(item) -> dict`` — comparable attributes (``created``,
      ``modified``, ``size_bytes``, ...) the validator diffs against the target;
    - ``read_version_history(item) -> (label, older)`` — the current version
      label and the older versions (oldest first, current excluded), used by a
      version-preserving target (the server-side package target) so history
      survives the migration;
    - ``supports_attachments`` — a class attribute set True by a source that
      emits list-item attachments as extra ``item_type="attachment"`` items.

    Absent when the source does not expose them.
    """

    @abstractmethod
    def list_items(self, progress: MigrationProgress = None) -> list[MigrationItem]:
        """Enumerate the items to migrate (with per-item progress)."""

    @abstractmethod
    def read(self, item: MigrationItem) -> object:
        """Read the payload for an item (bytes for files, dict for records)."""

    @abstractmethod
    def checksum(self, item: MigrationItem) -> str:
        """Content hash of an item, used for idempotency and verification."""


class DataTarget(ABC):
    """Writes migration items to a target.

    Optional hooks (not declared here so ``hasattr`` reflects real support):

    - ``configure(options)`` — called once by the runner before any write, so a
      target can derive per-run policy (e.g. a record target maps
      ``options.conflict_resolution`` onto its ``on_conflict`` mode);
    - ``apply_timestamps(item)`` / ``apply_authorship(item)`` /
      ``apply_permissions(item, permissions)`` — best-effort fidelity applied
      after a successful write;
    - ``read_permissions(item)`` / ``read_metadata(item)`` — the read
      counterparts the validator diffs against the source (needed to *verify*
      that the requested fidelity actually landed);
    - ``supports_versions`` — a class attribute set True by a target that can
      restore version history (the server-side package target). The runner then
      reads ``source.read_version_history(item)`` into ``item.version_label`` /
      ``item.versions`` before the write, so history is preserved whenever the
      source can supply it;
    - ``supports_authorship`` — a class attribute set True by a target that
      restores ``Author``/``ModifiedBy`` while building the payload (the
      server-side package target); client-side targets expose ``apply_authorship``
      instead (both best-effort, resolved users only);
    - ``supports_attachments`` — a class attribute set True by a target that
      accepts ``item_type="attachment"`` items.
    """

    @abstractmethod
    def exists(self, item: MigrationItem) -> bool:
        """Whether the item's destination already exists."""

    @abstractmethod
    def write(self, item: MigrationItem, payload: object) -> None:
        """Write the item's payload to its destination."""

    def write_many(
        self,
        items: list[MigrationItem],
        payloads: list[object],
        concurrency: int = 1,
    ) -> list:
        """Bulk-write a batch; the default falls back to per-item :meth:`write`.

        Targets that support true parallel writes (e.g. the SharePoint library
        target) override this. Returns a list of ``(path, error)`` failures.
        """
        for item, payload in zip(items, payloads):
            self.write(item, payload)
        return []

    @abstractmethod
    def list_paths(self) -> Iterable[str]:
        """Return all destination paths present on the target (for verification)."""

    @abstractmethod
    def checksum(self, item: MigrationItem) -> str:
        """Content hash of an item already on the target."""


def resolve_dest(item: MigrationItem, target: DataTarget, conflict: ConflictResolution) -> str:
    """Resolve a destination path honoring the conflict-resolution policy.

    ``SKIP`` keeps the original dest (the caller decides whether to skip);
    ``OVERWRITE`` and ``RENAME`` return the effective destination (RENAME appends
    a numeric suffix while the name collides).
    """
    dest = item.dest_path
    if conflict != ConflictResolution.RENAME:
        return dest
    probe = MigrationItem(item.source_path, dest, item.size_bytes, item.item_type)
    if not target.exists(probe):
        return dest
    base, dot, ext = dest.rpartition(".")
    counter = 1
    while True:
        candidate = f"{base}-{counter}{dot}{ext}" if dot else f"{base}-{counter}"
        if not target.exists(MigrationItem(item.source_path, candidate, item.size_bytes, item.item_type)):
            return candidate
        counter += 1
