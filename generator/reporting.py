"""Human-readable summary and JSON report for a generation run."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Optional, Sequence

from generator.manifest import MetadataChanges

if TYPE_CHECKING:
    from generator.builders.type import TypeBuilder

Planned = Sequence[tuple[str, "TypeBuilder"]]


@dataclass
class Reporter:
    """Prints the run summary and writes the optional JSON report."""

    metadata_path: str
    report_path: Optional[str] = None
    dry_run: bool = False

    def summary(self, planned: Planned, skipped_new: int, unrouted: list[str]) -> None:
        """Print the created/updated/skipped counts and the first unrouted types."""
        created = sum(1 for _, builder in planned if builder.status == "created")
        updated = sum(1 for _, builder in planned if builder.status == "updated")
        prefix = "[dry-run] " if self.dry_run else ""
        print(
            f"\n{prefix}planned: {created} created, {updated} updated; "
            f"skipped: {skipped_new} new (update-only), {len(unrouted)} unrouted"
        )
        if unrouted:
            print("  Skipped types (first 15):")
            for name in unrouted[:15]:
                print(f"    {name}")

    def metadata_changes(self, changes: MetadataChanges) -> None:
        """Report metadata deletions (kept in code — never auto-removed)."""
        if changes.is_empty:
            return
        print("\nMetadata removed since the last sync (kept in code):")
        if changes.removed_types:
            shown = ", ".join(changes.removed_types[:10])
            print(f"  {len(changes.removed_types)} type(s): {shown}")
        if changes.removed_members:
            total = sum(len(members) for members in changes.removed_members.values())
            print(f"  {total} member(s) across {len(changes.removed_members)} type(s):")
            for name, members in list(changes.removed_members.items())[:15]:
                print(f"    {name}: {', '.join(members)}")

    def write(self, planned: Planned, unrouted: list[str], changes: MetadataChanges) -> None:
        """Write the JSON run report, when a path was configured."""
        if not self.report_path:
            return
        payload = {
            "metadata": self.metadata_path,
            "created": [name for name, builder in planned if builder.status == "created"],
            "updated": [name for name, builder in planned if builder.status == "updated"],
            "skipped_unrouted": unrouted,
            "removed_types": changes.removed_types,
            "removed_members": changes.removed_members,
        }
        Path(self.report_path).write_text(json.dumps(payload, indent=2), encoding="utf-8")
        print(f"\nReport written to {self.report_path}")
