"""Migration delta — what changed at the source since the previous plan.

The manifest is the persisted plan ("what to migrate"). On a re-run a fresh plan
is compared against the one a previous run wrote, so a copy that is re-driven can
*name* the drift it cannot converge by itself:

- **missing** — planned before, gone from the source now: the target copy is an
  orphan (a re-run never deletes, because a target may legitimately hold content
  a copy did not put there);
- **moved** — the same source identity (a file's ``UniqueId``) now lives under a
  different path: the source was renamed/moved, and the previous target copy
  stays where it was, so the re-run would otherwise duplicate it;
- **changed** — the same path with a different modification time: with the
  ``skip`` conflict policy (the default) an existing target copy is left as it
  was, so the edit does not travel;
- **added** — in the new plan only: genuinely new, or never copied before.

Detection is deliberately side-effect free: nothing is deleted or moved on the
target. The report is data (:meth:`DeltaReport.to_dict`) plus human notes
(:meth:`DeltaReport.notes`), so drift is surfaced instead of being guessed at.

Identity limits are stated rather than papered over. A move is only recognizable
when the source exposes a stable identity (SharePoint files carry ``UniqueId``);
a renamed *folder* has none, so it shows up as one missing path plus the paths of
its moved children, and a list item is keyed by its source item id — retitling it
keeps the key, so it is reported as ``changed`` rather than ``moved``.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from office365.runtime.converters.scalars import parse_datetime

if TYPE_CHECKING:
    from collections.abc import Iterable

    from office365.migration.base import MigrationItem

__all__ = ["DeltaReport", "MovedItem", "compute_delta"]

#: Paths named in a note before it truncates to "and N more".
_NOTE_SAMPLE = 5


@dataclass
class MovedItem:
    """A planned item whose source identity reappeared under another path."""

    source_id: str
    from_path: str
    to_path: str

    @property
    def label(self) -> str:
        return f"{self.from_path} -> {self.to_path}"


@dataclass
class DeltaReport:
    """The drift between a previous plan and the current one.

    ``baseline`` is the number of items in the previous plan, or ``None`` when
    there was no readable previous plan (a first run). ``note`` explains a
    baseline that exists but could not be read, so an absent comparison is never
    mistaken for "nothing changed".
    """

    baseline: int | None = None
    note: str | None = None
    added: list[str] = field(default_factory=list)
    missing: list[str] = field(default_factory=list)
    moved: list[MovedItem] = field(default_factory=list)
    changed: list[str] = field(default_factory=list)

    @property
    def has_baseline(self) -> bool:
        """Whether a previous plan was available to compare against."""
        return self.baseline is not None

    @property
    def is_empty(self) -> bool:
        """Whether nothing drifted (or there was nothing to compare)."""
        return not (self.added or self.missing or self.moved or self.changed)

    @property
    def is_stale(self) -> bool:
        """Whether the target is known to differ from the source because of drift.

        ``added`` and ``changed`` alone do not qualify: an addition is copied by
        the re-run, and a change is re-applied by an incremental one. A deletion
        or a rename/move is what a copy cannot converge on its own.
        """
        return bool(self.missing or self.moved)

    def summary(self) -> str:
        if self.baseline is None:
            return "delta: no previous plan"
        return (
            f"delta vs {self.baseline} planned item(s): "
            f"{len(self.added)} new, {len(self.missing)} gone, "
            f"{len(self.moved)} moved, {len(self.changed)} changed"
        )

    def notes(self) -> list[str]:
        """Human-readable notes, one per kind of drift (empty when there is none)."""
        notes: list[str] = []
        if self.note:
            notes.append(f"delta unavailable: {self.note}")
        if self.missing:
            notes.append(
                f"{len(self.missing)} item(s) were planned by the previous run but are gone from "
                f"the source; a re-run does not delete their target copies: {_shown(self.missing)}"
            )
        if self.moved:
            notes.append(
                f"{len(self.moved)} item(s) were renamed or moved at the source; the previous "
                f"target copy stays at its old path: {_shown([move.label for move in self.moved])}"
            )
        if self.changed:
            notes.append(
                f"{len(self.changed)} item(s) changed at the source; under the skip conflict "
                f"policy an existing target copy is left as it was: {_shown(self.changed)}"
            )
        return notes

    def to_dict(self) -> dict[str, Any]:
        """A JSON-serializable projection of the report."""
        return {
            "baseline": self.baseline,
            "note": self.note,
            "added": list(self.added),
            "missing": list(self.missing),
            "moved": [{"source_id": m.source_id, "from": m.from_path, "to": m.to_path} for m in self.moved],
            "changed": list(self.changed),
        }


def compute_delta(
    previous: "Iterable[MigrationItem] | None",
    current: "Iterable[MigrationItem]",
    note: str | None = None,
) -> DeltaReport:
    """Diff a previous plan against the current one.

    Args:
        previous: The items a previous run planned, or ``None`` when there is no
            previous plan to compare against.
        current: The items the current plan produced.
        note: Why a ``previous`` that was expected could not be used (a corrupt
            manifest, say). It is carried into :attr:`DeltaReport.note` so the
            gap is reported rather than silently read as "no drift".
    """
    prior = list(previous) if previous is not None else None
    report = DeltaReport(baseline=None if prior is None else len(prior), note=note)
    if not prior:
        return report

    now = list(current)
    now_paths = {item.dest_path for item in now}
    # Identity is the only way to tell "renamed" from "deleted then created": a
    # source item keeps it across a rename/move, and it is absent for item kinds
    # whose plan key already *is* the identity (list items) or that carry none.
    now_by_identity = {item.source_id: item for item in now if item.source_id}
    prior_paths = {item.dest_path for item in prior}
    moved_targets: set[str] = set()
    for item in prior:
        successor = now_by_identity.get(item.source_id) if item.source_id else None
        if successor is not None and successor.dest_path != item.dest_path:
            # Identity wins over the path: the same source item lives elsewhere now.
            report.moved.append(MovedItem(item.source_id or "", item.dest_path, successor.dest_path))
            moved_targets.add(successor.dest_path)
            continue
        if item.dest_path in now_paths:
            continue
        report.missing.append(item.dest_path)

    prior_by_path = {item.dest_path: item for item in prior}
    report.added = sorted(path for path in now_paths - prior_paths if path not in moved_targets)
    report.missing.sort()
    report.moved.sort(key=lambda move: (move.from_path, move.to_path))
    for item in now:
        planned = prior_by_path.get(item.dest_path)
        if planned is None or not (planned.modified and item.modified):
            continue
        if not _same_instant(planned.modified, item.modified):
            report.changed.append(item.dest_path)
    report.changed.sort()
    return report


def _same_instant(left: str, right: str) -> bool:
    """Whether two timestamps denote the same moment (tolerant of formatting)."""
    left_dt, right_dt = parse_datetime(left), parse_datetime(right)
    if left_dt is None or right_dt is None:
        return left == right
    return left_dt == right_dt


def _shown(names: list[str]) -> str:
    shown = ", ".join(names[:_NOTE_SAMPLE])
    if len(names) > _NOTE_SAMPLE:
        shown = f"{shown} and {len(names) - _NOTE_SAMPLE} more"
    return shown
