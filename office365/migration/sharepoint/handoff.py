"""Detect the SharePoint artifacts a client-side copy cannot carry.

A same-tenant SPO→SPO migration moves content, structure and as much metadata and
security as REST allows. Some artifacts are simply outside that reach — publishing
pages, pages with no copyable body, and the web part data bindings modern pages
serialize (see :mod:`~office365.migration.sharepoint.pages`), workflow
associations, InfoPath forms, and business-data (BCS) external lists.
Copying content and then saying nothing about them is the unethical part: a site
that looks migrated silently loses its approval flow, its custom forms and its
external lists. This module keeps the gap honest by *reporting* them, so a run
never leaves a silent hole.

Every detector is read-only and cheap: the per-list signals (form URLs and
workflow associations) come from **one** projected request per web
(``$select`` of the form properties + ``$expand=WorkflowAssociations``), and the
site workflows from **one** more. Detection is best-effort by design — a failed
detector degrades to a warning in :attr:`SiteHandoff.failures` and never aborts
the migration.

Classification is deliberately narrow, because a false positive is worse than a
miss (both are reported, one is noise):

* a list form is an InfoPath form only when its URL names ``FormServer.aspx``,
  ``XsnLocation=`` or an ``.xsn`` file — the standard platform forms
  (``Forms/Upload.aspx``, ``Lists/X/NewForm.aspx``, ``_layouts/15/aclinv.aspx``,
  ...) never match;
* a workflow is reported when the list/site really carries an *association* —
  a template that is not attached to anything changes nothing;
* BCS is detected at list granularity (an external list, template 600). A column
  bound to an external content type is reported by the structure replay instead,
  which is where it would otherwise fail (see
  :func:`office365.migration.sharepoint.structure.provision_list_structure`).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Dict, Iterable, List, Optional

from office365.migration.sharepoint.pages import (
    PageCopyReport,
    PageHandoff,
    detect_page_handoff,
    page_handoff_note,
)

if TYPE_CHECKING:
    from office365.sharepoint.lists.list import List as SPList
    from office365.sharepoint.webs.web import Web

#: ``SPListTemplateType.ExternalList`` (MS-WSSTS 2.7) — a list whose rows live in
#: an external business-data (BCS) system. Its structure is a view over a BDC
#: model that a client-side copy cannot provision, so it is reported, not migrated.
EXTERNAL_LIST_TEMPLATE = 600

#: Fragments that mark a list form as a browser-enabled InfoPath form. InfoPath
#: browser forms are served by ``FormServer.aspx`` with the template in
#: ``XsnLocation``; a client-only form is an ``.xsn`` file.
_INFOPATH_FORM_MARKERS = ("formserver.aspx", "xsnlocation=", ".xsn")

#: The list properties that advertise a (possibly custom) form.
_FORM_URL_PROPERTIES = ("DefaultNewFormUrl", "DefaultEditFormUrl", "DefaultDisplayFormUrl")

#: The one projected read the per-list detectors share.
_LIST_SELECT = ["Title", "BaseTemplate", "Hidden", "DefaultNewFormUrl", "DefaultEditFormUrl", "DefaultDisplayFormUrl"]

#: Names shown inline in a note before it is truncated.
_MAX_NAMES_IN_NOTE = 5


@dataclass
class WorkflowFinding:
    """A workflow association a copy would not carry."""

    name: str
    #: The title of the list the workflow is bound to, or ``"site"``.
    scope: str

    @property
    def label(self) -> str:
        return f"{self.name} ({self.scope})"


@dataclass
class FormFinding:
    """A list whose declared form is an InfoPath form."""

    list_title: str
    urls: List[str] = field(default_factory=list)


@dataclass
class SiteHandoff:
    """Everything a whole-site migration leaves for out-of-band remediation."""

    pages: PageHandoff = field(default_factory=PageHandoff)
    workflows: List[WorkflowFinding] = field(default_factory=list)
    forms: List[FormFinding] = field(default_factory=list)
    external_lists: List[str] = field(default_factory=list)
    failures: List[str] = field(default_factory=list)

    @property
    def is_empty(self) -> bool:
        return not (self.pages.libraries or self.workflows or self.forms or self.external_lists)


def is_infopath_form_url(url: Optional[str]) -> bool:
    """Whether a list form URL designates an InfoPath form."""
    text = (url or "").casefold()
    return any(marker in text for marker in _INFOPATH_FORM_MARKERS)


def _association_properties(item: Any) -> Dict[str, Any]:
    """Read an expanded association's properties (a typed entity or raw JSON)."""
    if isinstance(item, dict):
        return item
    return item.properties


def _expanded_items(value: Any) -> List[Any]:
    """The items of an expanded navigation property, in any of its wire shapes.

    ``$expand`` deserializes into a loaded entity collection, but a raw payload
    (or a test double) may present a list or a ``{"results": [...]}`` envelope.
    """
    if value is None:
        return []
    if isinstance(value, dict):
        results = value.get("results")
        return list(results) if isinstance(results, list) else []
    return list(value)


def workflow_findings(scope: str, associations: Any) -> List[WorkflowFinding]:
    """Workflow associations bound to ``scope`` (a list title or ``"site"``)."""
    findings = []
    for item in _expanded_items(associations):
        name = _association_properties(item).get("Name")
        if name:
            findings.append(WorkflowFinding(name=str(name), scope=scope))
    return findings


def _form_urls(properties: Dict[str, Any]) -> List[str]:
    """The InfoPath form URLs a list declares (order-preserving, de-duplicated)."""
    urls: List[str] = []
    for name in _FORM_URL_PROPERTIES:
        url = properties.get(name)
        if is_infopath_form_url(url):
            urls.append(str(url))
    return list(dict.fromkeys(urls))


def _site_workflows(web: "Web") -> List[WorkflowFinding]:
    """Site-scoped workflow associations (one request)."""
    return workflow_findings("site", web.workflow_associations.get().execute_query())


def _list_signals(web: "Web") -> Iterable[Any]:
    """One projected read: every list's form URLs and workflow associations."""
    return web.lists.select(_LIST_SELECT).expand(["WorkflowAssociations"]).get().execute_query()


def _collect_list_signals(web: "Web", handoff: SiteHandoff) -> None:
    for sp_list in _list_signals(web):
        properties = sp_list.properties
        if properties.get("Hidden"):
            continue
        title = str(properties.get("Title") or "")
        if not title:
            continue
        handoff.workflows.extend(workflow_findings(title, properties.get("WorkflowAssociations")))
        urls = _form_urls(properties)
        if urls:
            handoff.forms.append(FormFinding(list_title=title, urls=urls))
        if properties.get("BaseTemplate") == EXTERNAL_LIST_TEMPLATE:
            handoff.external_lists.append(title)


def detect_handoff(web: "Web", lists: Iterable["SPList"]) -> SiteHandoff:
    """Detect what a whole-site migration of ``web`` would leave behind.

    ``lists`` is the web's already-loaded list collection, so page detection needs
    no extra query. Each detector is independently best-effort: a failure lands in
    :attr:`SiteHandoff.failures` and the remaining detectors still run.
    """
    handoff = SiteHandoff()
    try:
        handoff.pages = detect_page_handoff(lists)
    except Exception as exc:  # noqa: BLE001 - detection is best-effort; never abort the run
        handoff.failures.append(f"page detection failed: {exc}")
    try:
        handoff.workflows.extend(_site_workflows(web))
    except Exception as exc:  # noqa: BLE001 - detection is best-effort; never abort the run
        handoff.failures.append(f"site workflow detection failed: {exc}")
    try:
        _collect_list_signals(web, handoff)
    except Exception as exc:  # noqa: BLE001 - detection is best-effort; never abort the run
        handoff.failures.append(f"list workflow/form detection failed: {exc}")
    return handoff


def _shown(names: List[str]) -> str:
    """The first few names, with a ``+N more`` tail."""
    shown = ", ".join(names[:_MAX_NAMES_IN_NOTE])
    if len(names) > _MAX_NAMES_IN_NOTE:
        shown += f", +{len(names) - _MAX_NAMES_IN_NOTE} more"
    return shown


def handoff_notes(handoff: SiteHandoff, page_report: Optional[PageCopyReport] = None) -> List[str]:
    """One warning per handoff category, plus one per failed detector.

    Each note names what a *copy* cannot carry and asks for out-of-band
    remediation, so a migrated site never silently loses a flow or a form. Pass
    ``page_report`` when the pages were copied: only the pages with no copyable
    body are left over then, and the copy labels its own gaps (web part bindings,
    wiki markup that still points at the source site).
    """
    notes: List[str] = []
    page_note = page_handoff_note(handoff.pages, modern_copied=page_report is not None)
    if page_note:
        notes.append(page_note)
    if handoff.workflows:
        labels = sorted(finding.label for finding in handoff.workflows)
        notes.append(f"{len(labels)} workflow(s) are not migrated — remediate out of band: {_shown(labels)}")
    if handoff.forms:
        labels = sorted(f"{finding.list_title} ({len(finding.urls)} form(s))" for finding in handoff.forms)
        notes.append(
            f"{len(labels)} list(s) use an InfoPath form, which is not migrated — "
            f"remediate out of band: {_shown(labels)}"
        )
    if handoff.external_lists:
        titles = sorted(handoff.external_lists)
        notes.append(
            f"{len(titles)} business-data (BCS) external list(s) are not migrated — "
            f"remediate out of band: {_shown(titles)}"
        )
    notes.extend(handoff.failures)
    return notes


__all__ = [
    "EXTERNAL_LIST_TEMPLATE",
    "FormFinding",
    "SiteHandoff",
    "WorkflowFinding",
    "detect_handoff",
    "handoff_notes",
    "is_infopath_form_url",
    "workflow_findings",
]
