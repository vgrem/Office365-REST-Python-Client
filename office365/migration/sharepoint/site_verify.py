"""Reconcile a migrated web against its source in one read-only report.

Each web-scope concern the whole-site resolver touches has its own verifier —
:func:`verify_web_settings`, :func:`verify_web_branding`,
:func:`compare_web_scope_structure`, :func:`compare_site_scope`,
:func:`verify_navigation`, :func:`verify_page_copy`, :func:`verify_site_security`
and per list :func:`verify_list_structure`. Calling them one by one is what the
example did, which makes it easy to forget one and impossible to answer "did this
web migrate?" with a single value.

:func:`verify_site` folds them into a :class:`SiteVerificationReport`: one
``ok`` flag, one ``summary()`` line, and a JSON-serializable ``to_dict()`` for an
evidence pack. It performs **no writes** — every check issues GETs only.

Only the checks a run actually claims are run (a run without
``preserve_permissions`` does not report missing site groups as a mismatch), and a
check that *could not* run — an access denied, a web that cannot be read — lands in
``unverifiable`` rather than in the findings, so a partial verification never reads
as a pass.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Callable, Dict, Iterable, List, Optional, Tuple

from office365.migration.sharepoint.branding import verify_web_branding
from office365.migration.sharepoint.navigation import verify_navigation
from office365.migration.sharepoint.pages import verify_page_copy
from office365.migration.sharepoint.security import verify_list_security, verify_site_security
from office365.migration.sharepoint.site_scope import compare_site_scope, site_scope_note
from office365.migration.sharepoint.site_settings import verify_web_settings
from office365.migration.sharepoint.structure import (
    compare_web_scope_structure,
    web_scope_note,
)
from office365.migration.sharepoint.verify import StructureReport, verify_list_structure

if TYPE_CHECKING:
    from office365.sharepoint.client_context import ClientContext
    from office365.sharepoint.lists.list import List as SPList
    from office365.sharepoint.webs.web import Web

__all__ = ["LIST_SECURITY", "SITE_SCOPE", "SiteVerificationReport", "WEB_SCOPE_STRUCTURE", "verify_site"]

WEB_SCOPE_STRUCTURE = "web-scope structure"

#: Check name for a list's own ACL (as opposed to the web's or an item's).
LIST_SECURITY = "list security"

#: Check name for the site-level scope a migration never replays (features, regional settings).
SITE_SCOPE = "site scope"


def _web_url(web: "Web") -> str:
    """The web's URL, falling back to the context's base URL (a projected read drops it)."""
    for getter in ("url", "server_relative_url"):
        value = getattr(web, getter, None)
        if value:
            return str(value)
    context = getattr(web, "context", None)
    return str(getattr(context, "base_url", "") or "")


def _site_scope_findings(source_context: "ClientContext", target_context: "ClientContext") -> List[str]:
    """The features/regional settings the target lacks, as notes (empty = nothing missing)."""
    note = site_scope_note(compare_site_scope(source_context, target_context), _web_url(source_context.web))
    return [note] if note else []


def _web_scope_findings(source_web: "Web", target_web: "Web") -> List[str]:
    """The web-scope structure the target lacks, as notes (empty = nothing missing)."""
    note = web_scope_note(compare_web_scope_structure(source_web, target_web), _web_url(source_web))
    return [note] if note else []


@dataclass
class SiteVerificationReport:
    """What a migrated web still lacks, per dimension, in one place."""

    url: str = ""
    lists: List[StructureReport] = field(default_factory=list)
    checked: List[str] = field(default_factory=list)
    findings: Dict[str, List[str]] = field(default_factory=dict)
    unverifiable: List[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        """Whether any check contradicted the target (a check that could not run does not)."""
        return not self.findings and all(report.ok for report in self.lists)

    @property
    def complete(self) -> bool:
        """Whether every requested check actually ran."""
        return not self.unverifiable

    @property
    def issues(self) -> List[str]:
        """Every finding, flattened (dimension names are already in the notes)."""
        notes = [note for notes in self.findings.values() for note in notes]
        for report in self.lists:
            if not report.ok:
                notes.append(report.summary())
        return notes

    def summary(self) -> str:
        """One line: the verdict, then the per-dimension finding counts."""
        status = "OK" if self.ok else "MISMATCH"
        if not self.complete:
            status = f"PARTIAL {status}" if self.findings else "PARTIAL"
        parts = [f"{name}: {len(self.findings.get(name, []))}" for name in self.checked]
        if self.lists:
            failed = sum(1 for report in self.lists if not report.ok)
            parts.insert(0, f"lists: {len(self.lists)} ({failed} with issues)")
        detail = ", ".join(parts) if parts else "nothing to check"
        url = f" {self.url}" if self.url else ""
        return f"{status} |{url} | {detail}"

    def to_dict(self) -> Dict[str, Any]:
        """A JSON-serializable form (for reports/evidence packs)."""
        return {
            "url": self.url,
            "ok": self.ok,
            "complete": self.complete,
            "checked": list(self.checked),
            "lists": [report.to_dict() for report in self.lists],
            "findings": {name: list(notes) for name, notes in self.findings.items()},
            "unverifiable": list(self.unverifiable),
        }


def verify_site(
    source_context: "ClientContext",
    target_context: "ClientContext",
    *,
    lists: Optional[Iterable[Tuple["SPList", "SPList"]]] = None,
    structure: bool = True,
    web_scope_structure: bool = True,
    navigation: bool = False,
    pages: bool = False,
    security: bool = False,
    settings: bool = True,
    branding: bool = True,
    site_scope: bool = True,
) -> SiteVerificationReport:
    """Verify a migrated web against its source (read-only).

    Args:
        source_context: The source web's context.
        target_context: The target web's context.
        lists: ``(source_list, target_list)`` pairs to reconcile structurally. Only
            passed when the caller wants the container compared too; capture is
            performed here (:func:`verify_list_structure`).
        structure: Whether to reconcile the ``lists`` pairs (ignored without pairs).
        web_scope_structure: Report the site columns/content types the target web
            does not define (structure replay is per list, so this is a note about
            web scope, not a per-list failure).
        navigation: Reconcile quick launch and top navigation.
        pages: Reconcile modern site page copies.
        security: Reconcile custom site groups, web role assignments and each
            list's own ACL (a source list that restricts access the target list
            does not is the finding that matters).
        settings: Reconcile the web's ``Title``/``Description``.
        branding: Reconcile the web's master page, logo, alternate CSS and theme
            folder (compared source-path-rebased).
        site_scope: Report the features activated on the source site (web and site
            collection) that the target does not have, and the regional settings
            that differ. Read-only: neither is replayed by a migration.

    Returns:
        A :class:`SiteVerificationReport`; a check that raises is recorded in
        ``unverifiable`` instead of aborting the others.
    """
    source_web: "Web" = source_context.web
    target_web: "Web" = target_context.web
    report = SiteVerificationReport(url=_web_url(target_web))

    if lists is not None and structure:
        for source_list, target_list in lists:
            try:
                report.lists.append(verify_list_structure(source_list, target_list))
            except Exception as e:  # noqa: BLE001 — one unreadable list must not hide the rest
                report.unverifiable.append(f"list structure for {getattr(source_list, 'title', '?')}: {e}")

    checks: Dict[str, Tuple[Callable[[], List[str]], bool]] = {
        "settings": (lambda: verify_web_settings(source_web, target_web), settings),
        "branding": (lambda: verify_web_branding(source_web, target_web), branding),
        WEB_SCOPE_STRUCTURE: (lambda: _web_scope_findings(source_web, target_web), web_scope_structure),
        SITE_SCOPE: (lambda: _site_scope_findings(source_context, target_context), site_scope),
        "navigation": (lambda: verify_navigation(source_web, target_web), navigation),
        "pages": (lambda: verify_page_copy(source_web, target_web), pages),
        "security": (lambda: verify_site_security(source_web, target_web), security),
        # A list's own ACL is a separate scope from the web's (and from an item's).
        LIST_SECURITY: (lambda: verify_list_security(source_web, target_web), security),
    }
    for name, (run, enabled) in checks.items():
        if not enabled:
            continue
        report.checked.append(name)
        try:
            notes = run()
        except Exception as e:  # noqa: BLE001 — a check that cannot run is reported, not raised
            report.unverifiable.append(f"{name}: {e}")
            continue
        if notes:
            report.findings[name] = list(notes)
    return report
