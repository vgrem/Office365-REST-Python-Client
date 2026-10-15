"""Fidelity negotiation — describe what a run will (and won't) preserve.

A migration can request fidelity flags (timestamps, permissions, versions) that a
given adapter pair cannot honor. The runner fails fast on such a flag
(:func:`office365.migration.runner._assert_fidelity_supported`) instead of
silently migrating without it, but a caller usually wants to *report* the
capability **before** a run rather than discover it mid-flight.

:func:`describe_fidelity` inspects the optional adapter hooks and returns a
:class:`FidelityReport`; it never mutates the adapters and never raises.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from office365.migration.base import MigrationOptions

__all__ = ["FidelityReport", "describe_fidelity"]


@dataclass
class FidelityReport:
    """Which requested fidelity flags an adapter pair can honor.

    Attributes:
        preserved: Requested flags the pair can apply.
        unsupported: Requested flags the pair cannot apply (the run would fail).
        not_requested: Known flags not requested (informational).
        notes: A human-readable reason for each unsupported flag.
    """

    preserved: list[str] = field(default_factory=list)
    unsupported: list[str] = field(default_factory=list)
    not_requested: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        """Whether every *requested* fidelity flag can be honored."""
        return not self.unsupported

    def to_dict(self) -> dict[str, Any]:
        """A JSON-serializable form (for reports / session status)."""
        return {
            "preserved": list(self.preserved),
            "unsupported": list(self.unsupported),
            "not_requested": list(self.not_requested),
            "notes": list(self.notes),
            "ok": self.ok,
        }

    def summary(self) -> str:
        """A one-line, human-readable description of the report."""
        parts: list[str] = []
        if self.preserved:
            parts.append("preserved: " + ", ".join(self.preserved))
        if self.not_requested:
            parts.append("not requested: " + ", ".join(self.not_requested))
        if self.unsupported:
            parts.append("UNSUPPORTED: " + ", ".join(self.unsupported))
        return " | ".join(parts) if parts else "content only"


def _supports(obj: Any, name: str) -> bool:
    return callable(getattr(obj, name, None))


def describe_fidelity(source: Any, target: Any, options: MigrationOptions) -> FidelityReport:
    """Describe which requested fidelity flags the adapter pair can honor.

    Checks the optional hooks — ``DataSource.read_permissions(item)``,
    ``DataTarget.apply_timestamps(item)``, ``DataTarget.apply_permissions(item,
    permissions)``. Version history needs both a version-preserving target
    (``DataTarget.supports_versions``, i.e. the server-side package target) and a
    source that exposes ``read_version_history``; it is unsupported on the
    client-side REST path.

    Args:
        source: The source adapter.
        target: The target adapter.
        options: The migration options whose fidelity flags are being requested.

    Returns:
        A :class:`FidelityReport` (never raises).
    """
    report = FidelityReport()
    checks = (
        (
            "timestamps",
            options.preserve_timestamps,
            _supports(target, "apply_timestamps"),
            "target.apply_timestamps(item)",
        ),
        (
            "permissions",
            options.preserve_permissions,
            _supports(source, "read_permissions") and _supports(target, "apply_permissions"),
            "source.read_permissions(item) and target.apply_permissions(item, permissions)",
        ),
        (
            "versions",
            options.preserve_versions,
            bool(getattr(target, "supports_versions", False)) and _supports(source, "read_version_history"),
            "a version-preserving target (server-side Migration API) and source.read_version_history(item)",
        ),
    )
    for label, requested, supported, requirement in checks:
        if not requested:
            report.not_requested.append(label)
        elif supported:
            report.preserved.append(label)
        else:
            report.unsupported.append(label)
            report.notes.append(f"{label} needs {requirement}; this adapter pair does not provide it")
    return report
