"""Shared reconciliation report for the data pipeline and the migration toolkit.

One report type is returned by every ``verify*`` (``RecordCollection.verify``,
``List.verify``, ``ImportResult.verify`` and ``migration.verify``), so callers
reason about reconciliation the same way regardless of the operation.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class VerificationReport:
    """Outcome of a source-vs-target reconciliation.

    ``source_count``/``target_count`` are the expected/found item counts and
    ``checked`` the number of items checked. The four lists are disjoint buckets
    of findings:

    * ``missing`` — expected keys absent on the target;
    * ``extra`` — keys present on the target but not expected;
    * ``mismatches`` — an item exists on both sides but its content/metadata
      differs;
    * ``unverifiable`` — a requested check could not be run (the adapters expose
      no way to read the attribute, the service forbids it, ...).

    ``ok`` is True when the counts match and there are no missing/extra/mismatch
    findings; ``complete`` is stricter and also requires that no requested check
    was skipped as unverifiable.
    """

    source_count: int = 0
    target_count: int = 0
    checked: int = 0
    missing: list[str] = field(default_factory=list)
    extra: list[str] = field(default_factory=list)
    mismatches: list[str] = field(default_factory=list)
    unverifiable: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        """Whether the source and target reconcile (no discrepancies found)."""
        return self.source_count == self.target_count and not self.missing and not self.extra and not self.mismatches

    @property
    def complete(self) -> bool:
        """``ok`` and every requested check actually ran (no ``unverifiable``)."""
        return self.ok and not self.unverifiable

    def summary(self) -> str:
        status = "OK" if self.complete else ("PARTIAL" if self.ok else "MISMATCH")
        return (
            f"{status} | source: {self.source_count}, target: {self.target_count}, "
            f"checked: {self.checked}, missing: {len(self.missing)}, extra: {len(self.extra)}, "
            f"issues: {len(self.mismatches)}, unverifiable: {len(self.unverifiable)}"
        )

    def to_dict(self) -> dict[str, Any]:
        """A JSON-serializable form (for reports/evidence packs)."""
        return {
            "source_count": self.source_count,
            "target_count": self.target_count,
            "checked": self.checked,
            "missing": list(self.missing),
            "extra": list(self.extra),
            "mismatches": list(self.mismatches),
            "unverifiable": list(self.unverifiable),
            "ok": self.ok,
            "complete": self.complete,
        }
