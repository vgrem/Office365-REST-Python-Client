"""Fidelity negotiation — describe what a run will (and won't) preserve.

A migration can request fidelity flags (timestamps, permissions, versions) that a
given adapter pair cannot honor. The runner fails fast on such a flag
(:func:`office365.migration.runner._assert_fidelity_supported`) instead of
silently migrating without it, but a caller usually wants to *report* the
capability **before** a run rather than discover it mid-flight.

:func:`describe_fidelity` inspects the optional adapter hooks and returns a
:class:`FidelityReport`; it never mutates the adapters and never raises.

The report carries two views:

* the **requested-flag negotiation** (:attr:`FidelityReport.preserved` /
  ``unsupported`` / ``not_requested``) — what the run will honor, and what it
  will fail fast on; and
* a **fidelity matrix** (:attr:`FidelityReport.dimensions`) — every migration
  dimension the engine models, each reported ``delivered`` / ``best-effort`` /
  ``unsupported`` / ``handoff``, with a one-line reason in
  ``dimension_notes``. The matrix is broader than the requested flags: it also
  names dimensions no adapter carries (so their absence is explicit, never
  implicit), and is the machine-readable form of the table in ``docs/migration.md``.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from office365.migration.base import MigrationOptions

__all__ = ["FidelityReport", "FidelityStatus", "describe_fidelity"]


class FidelityStatus(str, Enum):
    """How well an adapter pair covers one fidelity dimension."""

    #: Copied faithfully.
    DELIVERED = "delivered"
    #: Copied, but with known, reported limits (e.g. same-tenant, resolved users).
    BEST_EFFORT = "best-effort"
    #: Not carried by the adapters; the caller must provision it another way.
    UNSUPPORTED = "unsupported"
    #: Detected on the source and handed off for out-of-band remediation.
    HANDOFF = "handoff"


@dataclass
class FidelityReport:
    """Which requested fidelity flags an adapter pair can honor, plus the matrix.

    Attributes:
        preserved: Requested flags the pair can apply.
        unsupported: Requested flags the pair cannot apply (the run would fail).
        not_requested: Known flags not requested (informational).
        notes: A human-readable reason for each unsupported flag.
        dimensions: Every modeled fidelity dimension → :class:`FidelityStatus`
            value (``delivered``/``best-effort``/``unsupported``/``handoff``).
        dimension_notes: A one-line reason for each dimension whose status is not
            ``delivered``.
    """

    preserved: list[str] = field(default_factory=list)
    unsupported: list[str] = field(default_factory=list)
    not_requested: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)
    dimensions: dict[str, str] = field(default_factory=dict)
    dimension_notes: dict[str, str] = field(default_factory=dict)

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
            "dimensions": dict(self.dimensions),
            "dimension_notes": dict(self.dimension_notes),
            "ok": self.ok,
        }

    def summary(self) -> str:
        """A one-line, human-readable description of the requested-flag negotiation."""
        parts: list[str] = []
        if self.preserved:
            parts.append("preserved: " + ", ".join(self.preserved))
        if self.not_requested:
            parts.append("not requested: " + ", ".join(self.not_requested))
        if self.unsupported:
            parts.append("UNSUPPORTED: " + ", ".join(self.unsupported))
        return " | ".join(parts) if parts else "content only"

    def matrix_summary(self) -> str:
        """A one-line, human-readable description of the fidelity matrix."""
        return ", ".join(f"{name}={status}" for name, status in self.dimensions.items())


def _supports(obj: Any, name: str) -> bool:
    return callable(getattr(obj, name, None))


def _dimensions(source: Any, target: Any) -> tuple[dict[str, str], dict[str, str]]:
    """The full fidelity matrix for an adapter pair (capability-probed, conservative)."""
    status = FidelityStatus
    dims: dict[str, str] = {}
    notes: dict[str, str] = {}

    def set_(name: str, value: FidelityStatus, note: str = "") -> None:
        dims[name] = value.value
        if note and value is not status.DELIVERED:
            notes[name] = note

    set_("content", status.DELIVERED)

    if getattr(target, "supports_versions", False) and _supports(source, "read_version_history"):
        set_(
            "versions",
            status.BEST_EFFORT,
            "history content is preserved; per-version author/timestamp are not carried",
        )
    else:
        set_(
            "versions",
            status.UNSUPPORTED,
            "needs a version-preserving target (server-side Migration API) and source.read_version_history(item)",
        )

    if _supports(target, "apply_timestamps"):
        set_("timestamps", status.DELIVERED)
    else:
        set_("timestamps", status.UNSUPPORTED, "target.apply_timestamps(item) is not implemented")

    if callable(getattr(target, "apply_authorship", None)) or getattr(target, "supports_authorship", False):
        set_(
            "authorship",
            status.BEST_EFFORT,
            "Author/ModifiedBy are applied for resolved users; principals without a known login are skipped",
        )
    else:
        set_("authorship", status.UNSUPPORTED, "needs an authorship-preserving target (server-side Migration API)")

    if _supports(source, "read_permissions") and _supports(target, "apply_permissions"):
        set_(
            "permissions",
            status.BEST_EFFORT,
            "same-tenant only; groups and principals without a PUID are skipped, and a "
            "list's own ACLs are replayed by apply_site_list_security after the content",
        )
    else:
        set_(
            "permissions",
            status.UNSUPPORTED,
            "needs source.read_permissions(item) and target.apply_permissions(item, permissions)",
        )

    if getattr(source, "supports_attachments", False) and getattr(target, "supports_attachments", False):
        set_("attachments", status.DELIVERED)
    else:
        set_("attachments", status.UNSUPPORTED, "list-item attachments are carried only between list adapters")

    set_(
        "structure",
        status.UNSUPPORTED,
        "columns, content types, views and list container settings are not carried by the adapters; "
        "replay them with provision_list_structure (the resolver does), which is per list: "
        "web-scope site columns and site content types are replayed only through the lists that use them",
    )
    set_(
        "content_types",
        status.UNSUPPORTED,
        "content types are not carried by the adapters; replay them with provision_list_structure "
        "(the resolver does) per list — web-scope registration of a site content type is not reproduced",
    )
    if getattr(source, "supports_typed_values", False) and getattr(target, "supports_typed_values", False):
        set_(
            "typed_values",
            status.BEST_EFFORT,
            "Lookup values are remapped across migrated lists and Person values by login, "
            "including multi-value columns; Managed Metadata values are carried by term id "
            "(the term store itself is not migrated); nested values are not carried",
        )
    else:
        set_(
            "typed_values",
            status.UNSUPPORTED,
            "record values are copied verbatim; lookup/person value remapping is not implemented",
        )
    if getattr(target, "supports_item_state", False):
        set_(
            "item_state",
            status.BEST_EFFORT,
            "approval status and its comments are carried for list items and document library files "
            "(the list/library must enable moderation); "
            "check-out and draft-version state are not",
        )
    else:
        set_("item_state", status.UNSUPPORTED, "check-out/draft/approval state is not carried")
    set_("views", status.UNSUPPORTED, "views are not carried by the adapters; replay them with provision_list_structure")
    set_(
        "navigation",
        status.BEST_EFFORT,
        "navigation and site pages are web-scope concerns the adapters do not carry: the whole-site "
        "resolver copies quick-launch/top-nav links (migrate_navigation) and both modern site pages "
        "(their canvas) and classic wiki pages (their WikiField body) with migrate_pages, and points "
        "the target web's home page at the copy of the source's; publishing pages, pages with no "
        "copyable body and web-part data bindings remain handoff",
    )
    set_(
        "site_settings",
        status.BEST_EFFORT,
        "each web's Title and Description are copied onto the target web when they differ "
        "(migrate_site_settings), as are the branding properties that REST accepts — master page, "
        "logo, alternate CSS and theme folder, rebased onto the target's path and only when the "
        "target has the asset they name; the site-collection/regional settings are not carried "
        "over REST",
    )
    set_("sharing_links", status.UNSUPPORTED, "sharing links follow the tenant policy; they are not recreated per item")
    return dims, notes


def describe_fidelity(source: Any, target: Any, options: MigrationOptions) -> FidelityReport:
    """Describe which requested fidelity flags the adapter pair can honor, plus the matrix.

    Checks the optional hooks — ``DataSource.read_permissions(item)``,
    ``DataTarget.apply_timestamps(item)``, ``DataTarget.apply_authorship(item)``,
    ``DataTarget.apply_permissions(item, permissions)``. Version history needs both
    a version-preserving target (``DataTarget.supports_versions``, i.e. the
    server-side package target) and a source that exposes ``read_version_history``;
    it is unsupported on the client-side REST path. Authorship needs
    ``DataTarget.apply_authorship`` (client-side) or ``supports_authorship`` (the
    server-side package target).

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
            "authorship",
            options.preserve_authorship,
            _supports(target, "apply_authorship") or bool(getattr(target, "supports_authorship", False)),
            "target.apply_authorship(item) or a supports_authorship target (server-side Migration API)",
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
    report.dimensions, report.dimension_notes = _dimensions(source, target)
    return report
