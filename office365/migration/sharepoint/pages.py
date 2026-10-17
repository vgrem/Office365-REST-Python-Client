"""Copy modern site pages, and detect the classic ones a client-side copy skips.

A page library (``base_template`` 119 — *Site Pages*, wiki or publishing pages)
holds ``.aspx`` pages rather than documents, so the item adapters do not migrate
it. **Modern** site pages are still reachable over REST, so this module copies
them: the page is created through the ``sitepages`` endpoint, its canvas and page
metadata are written onto the created item, and the page is published when the
source page was published. What a copy cannot fix is the *inside* of a web part —
a serialized client-side web part keeps the source list/library identifiers it
binds to, and those are not remapped.

Classic pages (wiki pages, publishing pages) and blank/unknown pages are
transformation work, not copy work: :func:`detect_page_handoff` inventories them
and :func:`page_handoff_note` names them, so a run never silently drops them.

Two facts this module relies on, both live-verified on a SharePoint Online tenant:

* ``POST /_api/sitepages/pages`` (``Web.add_site_page``) creates a modern page; a
  page created that way is a *draft* until
  ``POST /_api/sitepages/pages(<id>)/publish`` (``SitePage.publish``) runs, and a
  MERGE of ``OData__ModerationStatus`` does **not** publish it;
* a page's ``CanvasContent1`` round-trips byte-identical through
  ``item.set_property("CanvasContent1", ...)`` + ``item.update()``; a *newly
  created* page already carries a default empty canvas, which a MERGE of ``""``
  does not clear, so an empty source canvas is left alone and not verified.

Copies are add-only: an existing target page is never deleted, and the duplicate
behaviour is explicit (``RENAME`` by default, as SPMT does; ``SKIP`` and
``OVERWRITE`` are available).

:mod:`office365.migration.sharepoint.handoff` composes this module with the other
uncopyable artifacts (workflows, InfoPath forms, BCS external lists) and is what
the whole-site resolver actually calls.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Iterable, Optional

from office365.sharepoint.lists.templates.type import ListTemplateType
from office365.sharepoint.publishing.pages.canvas import count_web_parts

if TYPE_CHECKING:
    from office365.sharepoint.listitems.listitem import ListItem
    from office365.sharepoint.lists.list import List as SPList
    from office365.sharepoint.webs.web import Web

#: ``SPListTemplateType.WebPageLibrary`` — Site Pages, wiki and publishing pages.
PAGE_LIBRARY_TEMPLATE = ListTemplateType.WebPageLibrary.value

#: Modern site pages derive from this base content type, so a prefix match
#: identifies them without enumerating every derived page content type.
SITE_PAGE_CONTENT_TYPE_PREFIX = "0x0101009D1CB255DA76424F860D91F20E6C4118"

#: Duplicate handling for a page whose name already exists on the target. The
#: values are the SPMT ``DuplicatePageBehavior`` vocabulary.
DUPLICATE_RENAME = "RENAME"
DUPLICATE_SKIP = "SKIP"
DUPLICATE_OVERWRITE = "OVERWRITE"
_DUPLICATE_BEHAVIORS = (DUPLICATE_RENAME, DUPLICATE_SKIP, DUPLICATE_OVERWRITE)

#: Page content blobs; an empty string means "nothing to carry" (see the module docstring).
_CONTENT_FIELDS = ("CanvasContent1", "LayoutWebpartsContent")

#: The projected read a page copy needs: identity, the canvas, the layout, and the
#: page metadata the Site Pages library stores as list item properties.
_PAGE_SELECT = (
    "Id",
    "FileLeafRef",
    "Title",
    "Description",
    "ContentTypeId",
    "CanvasContent1",
    "LayoutWebpartsContent",
    "PromotedState",
    "BannerImageUrl",
    "OData__ModerationStatus",
)

#: A page whose ``Article`` canvas is empty is still readable, so detection needs
#: only the wiki field of a classic page.
_DETECT_SELECT = ("FileLeafRef", "ContentTypeId", "CanvasContent1", "WikiField")

#: Page names shown inline in the handoff note before it is truncated.
_MAX_PAGES_IN_NOTE = 5

#: Names shown inline in a copy warning before it is truncated.
_MAX_NAMES_IN_NOTE = 5


@dataclass
class PagePayload:
    """The page content and metadata a copy writes onto a created page.

    Property values are kept in their wire shape (``BannerImageUrl`` is a
    ``{"Url", "Description"}`` value object), so they can be written back verbatim.
    """

    name: str
    title: Optional[str] = None
    description: Optional[str] = None
    content_type_id: Optional[str] = None
    canvas: Optional[str] = None
    layout: Optional[str] = None
    banner_image_url: Optional[dict] = None
    promoted_state: Optional[int] = None
    #: Whether the source page was published (approved), so the copy should publish too.
    published: bool = True
    #: Client-side web parts serialized in the canvas (their bindings are not remapped).
    web_parts: int = 0

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "title": self.title,
            "description": self.description,
            "promoted_state": self.promoted_state,
            "published": self.published,
            "web_parts": self.web_parts,
            "canvas_length": len(self.canvas or ""),
        }


@dataclass
class PageInfo:
    """One page in a page library."""

    name: str
    kind: str  #: ``modern`` (has a canvas), ``classic`` (WikiField) or ``unknown``
    web_parts: int = 0


@dataclass
class PageLibrary:
    """A page library, with the pages it holds."""

    title: str
    pages: list[PageInfo] = field(default_factory=list)

    @property
    def web_part_count(self) -> int:
        return sum(page.web_parts for page in self.pages)

    @property
    def classic_pages(self) -> list[PageInfo]:
        return [page for page in self.pages if page.kind != "modern"]


@dataclass
class PageHandoff:
    """Everything a page copy leaves for out-of-band remediation."""

    libraries: list[PageLibrary] = field(default_factory=list)

    @property
    def page_count(self) -> int:
        return sum(len(library.pages) for library in self.libraries)

    @property
    def web_part_count(self) -> int:
        return sum(library.web_part_count for library in self.libraries)

    @property
    def classic_page_count(self) -> int:
        return sum(len(library.classic_pages) for library in self.libraries)

    @property
    def is_empty(self) -> bool:
        return self.page_count == 0


@dataclass
class PageCopyReport:
    """What a page copy did, and what it could not do."""

    #: Source page libraries considered, by title.
    libraries: list[str] = field(default_factory=list)
    #: Target page names written (already includes the renamed ones).
    copied: list[str] = field(default_factory=list)
    #: Target page names rewritten in place (``OVERWRITE``).
    overwritten: list[str] = field(default_factory=list)
    #: ``(source name, target name)`` pairs for pages renamed around a duplicate.
    renamed: list[tuple[str, str]] = field(default_factory=list)
    #: Pages left untouched because a page of that name already exists (``SKIP``).
    skipped: list[str] = field(default_factory=list)
    #: Pages published after their content was written.
    published: list[str] = field(default_factory=list)
    #: Pages whose canvas did not read back identical after the write.
    mismatched: list[str] = field(default_factory=list)
    #: ``(page name, error)`` for pages that could not be copied.
    failed: list[tuple[str, str]] = field(default_factory=list)
    #: Classic/unknown pages, left for page transformation.
    classic: list[str] = field(default_factory=list)
    #: Pages whose canvas serializes client-side web parts (bindings not remapped).
    web_part_pages: list[str] = field(default_factory=list)

    @property
    def page_count(self) -> int:
        return len(self.copied) + len(self.overwritten)

    @property
    def is_empty(self) -> bool:
        return self.page_count == 0

    def summary(self) -> Optional[str]:
        """One line describing what the copy did, or ``None`` when nothing happened."""
        if not self.copied and not self.overwritten and not self.skipped:
            return None
        parts = []
        if self.copied:
            detail = f"{len(self.copied)} page(s) copied"
            if self.renamed:
                detail += f" ({len(self.renamed)} renamed around an existing page)"
            parts.append(detail)
        if self.overwritten:
            parts.append(f"{len(self.overwritten)} overwritten")
        if self.skipped:
            parts.append(f"{len(self.skipped)} left as they were")
        if self.published:
            parts.append(f"{len(self.published)} published")
        return "page copy: " + ", ".join(parts)


def _shown(names: Iterable[str]) -> str:
    """The first few names, with a ``+N more`` tail."""
    names = list(names)
    shown = ", ".join(names[:_MAX_NAMES_IN_NOTE])
    if len(names) > _MAX_NAMES_IN_NOTE:
        shown += f", +{len(names) - _MAX_NAMES_IN_NOTE} more"
    return shown


def is_modern_page(content_type_id: Optional[str], canvas: Optional[str]) -> bool:
    """Whether a page is a modern site page (copyable) rather than a classic one."""
    return bool(canvas) or (content_type_id or "").startswith(SITE_PAGE_CONTENT_TYPE_PREFIX)


def _payload(properties: dict) -> PagePayload:
    """The copyable payload of a modern page, from its list item properties."""
    status = properties.get("OData__ModerationStatus")
    return PagePayload(
        name=str(properties.get("FileLeafRef") or ""),
        title=properties.get("Title"),
        description=properties.get("Description"),
        content_type_id=properties.get("ContentTypeId"),
        canvas=properties.get("CanvasContent1"),
        layout=properties.get("LayoutWebpartsContent"),
        banner_image_url=properties.get("BannerImageUrl"),
        promoted_state=properties.get("PromotedState"),
        published=status in (None, 0, "0"),
        web_parts=count_web_parts(properties.get("CanvasContent1")),
    )


def capture_page(item: "ListItem") -> Optional[PagePayload]:
    """The payload of a modern page item, or ``None`` for a classic/unknown page."""
    properties = item.properties
    name = properties.get("FileLeafRef") or ""
    if not name.lower().endswith(".aspx"):
        return None
    if not is_modern_page(properties.get("ContentTypeId"), properties.get("CanvasContent1")):
        return None
    return _payload(properties)


def _classify(sp_list: "SPList") -> tuple[list[PagePayload], list[str]]:
    """Read one page library once: (modern payloads, classic page names)."""
    payloads: list[PagePayload] = []
    classic: list[str] = []
    items = sp_list.items.select(list(_PAGE_SELECT)).get().execute_query()
    for item in items:
        properties = item.properties
        name = str(properties.get("FileLeafRef") or "")
        if not name.lower().endswith(".aspx"):
            continue
        if is_modern_page(properties.get("ContentTypeId"), properties.get("CanvasContent1")):
            payloads.append(_payload(properties))
        else:
            classic.append(name)
    return payloads, classic


def capture_site_pages(sp_list: "SPList") -> list[PagePayload]:
    """The modern pages of a page library (one projected read; read-only)."""
    return _classify(sp_list)[0]


def apply_page_payload(item: "ListItem", page: PagePayload) -> None:
    """Queue a MERGE of the page content onto ``item`` (execute the query after)."""
    values: dict[str, Any] = {
        "Title": page.title,
        "Description": page.description,
        "CanvasContent1": page.canvas,
        "LayoutWebpartsContent": page.layout,
        "BannerImageUrl": page.banner_image_url,
        "PromotedState": page.promoted_state,
    }
    for name, value in values.items():
        if value is None:
            continue
        if name in _CONTENT_FIELDS and not value:
            continue
        item.set_property(name, value)
    item.update()


def _is_page_library(sp_list: "SPList") -> bool:
    return bool(sp_list.base_template == PAGE_LIBRARY_TEMPLATE and not sp_list.hidden and sp_list.title)


def _page_libraries(lists: Iterable["SPList"]) -> list["SPList"]:
    return [sp for sp in lists if _is_page_library(sp)]


def _target_library(source_list: "SPList", target_libraries: list["SPList"]) -> Optional["SPList"]:
    """The target library that pairs with a source page library (title, else single)."""
    title = (source_list.title or "").casefold()
    for candidate in target_libraries:
        if (candidate.title or "").casefold() == title:
            return candidate
    return target_libraries[0] if len(target_libraries) == 1 else None


def _renamed(name: str, taken: set) -> str:
    """A free page name next to ``name`` (``Home.aspx`` -> ``Home-1.aspx``)."""
    stem, dot, extension = name.rpartition(".")
    if not dot:
        stem, extension = name, ""
    suffix = f".{extension}" if dot else ""
    index = 1
    while True:
        candidate = f"{stem}-{index}{suffix}"
        if candidate.casefold() not in taken:
            return candidate
        index += 1


def _batch(report: "PageCopyReport", behavior: str, name: str, taken: set, existing: dict) -> Optional[tuple]:
    """Decide the target page name and item id for one source page.

    Returns ``(source name, target name, item id or None)``; ``None`` means the page
    is deliberately left alone (``SKIP`` on an existing page).
    """
    if name.casefold() not in existing:
        return name, name, None
    if behavior == DUPLICATE_OVERWRITE:
        return name, name, existing[name.casefold()]
    if behavior == DUPLICATE_SKIP:
        report.skipped.append(name)
        return None
    target = _renamed(name, taken)
    return name, target, None


def _copy_page(
    target_web: "Web",
    target_list: "SPList",
    page: PagePayload,
    target_name: str,
    item_id: Optional[int],
) -> None:
    """Create or overwrite one page and publish it when the source page was."""
    if item_id is None:
        created = target_web.add_site_page(target_name, title=page.title)
        target_web.context.execute_query()
        item_id = created.properties.get("Id")
        if item_id is None:
            raise ValueError(f"the target did not return an id for the created page {target_name!r}")
    item = target_list.get_item_by_id(item_id)
    apply_page_payload(item, page)
    target_web.context.execute_query()
    if page.published:
        target_web.get_site_page_by_id(item_id).publish().execute_query()


def _verify(report: "PageCopyReport", target_list: "SPList", written: dict) -> None:
    """Read the copied pages back once and compare their canvases."""
    if not written:
        return
    items = target_list.items.select(["Id", "FileLeafRef", "CanvasContent1"]).get().execute_query()
    canvases = {
        str(item.properties.get("FileLeafRef") or "").casefold(): item.properties.get("CanvasContent1") for item in items
    }
    for name, canvas in written.items():
        if not canvas:
            continue
        if canvases.get(name.casefold()) != canvas:
            report.mismatched.append(name)


def copy_site_pages(
    source_web: "Web",
    target_web: "Web",
    *,
    duplicate_behavior: str = DUPLICATE_RENAME,
    warnings: Optional[list[str]] = None,
) -> PageCopyReport:
    """Copy the source web's modern site pages to the target web's page library.

    Read the source page libraries once each, create (or overwrite) the pages on
    the target, write the canvas and page metadata, publish the pages the source
    had published, and read the canvases back to verify the write. Classic pages
    are reported in :attr:`PageCopyReport.classic` because copying cannot
    transform them.

    Args:
        source_web: The web whose pages are captured (read-only).
        target_web: The web whose Site Pages library receives the pages.
        duplicate_behavior: What to do when a page of that name already exists —
            ``RENAME`` (default, as SPMT), ``SKIP`` or ``OVERWRITE``.
        warnings: Collected notes; problems the copy hit are appended here.
    """
    notes = warnings if warnings is not None else []
    report = PageCopyReport()
    behavior = (duplicate_behavior or DUPLICATE_RENAME).upper()
    if behavior not in _DUPLICATE_BEHAVIORS:
        notes.append(f"page copy: unknown duplicate behavior {duplicate_behavior!r}; using {DUPLICATE_RENAME}")
        behavior = DUPLICATE_RENAME
    source_libraries = _page_libraries(source_web.lists.get().execute_query())
    if not source_libraries:
        return report
    target_libraries = _page_libraries(target_web.lists.get().execute_query())
    for source_list in source_libraries:
        title = str(source_list.title or "")
        report.libraries.append(title)
        payloads, classic = _classify(source_list)
        report.classic.extend(classic)
        if not payloads:
            continue
        target_list = _target_library(source_list, target_libraries)
        if target_list is None:
            notes.append(f"page copy: no target page library matches '{title}' — {len(payloads)} page(s) not copied")
            continue
        existing = {
            str(item.properties.get("FileLeafRef") or "").casefold(): item.properties.get("Id")
            for item in target_list.items.select(["Id", "FileLeafRef"]).get().execute_query()
        }
        taken = set(existing)
        written: dict = {}
        for page in payloads:
            decision = _batch(report, behavior, page.name, taken, existing)
            if decision is None:
                continue
            source_name, target_name, item_id = decision
            try:
                _copy_page(target_web, target_list, page, target_name, item_id)
            except Exception as e:  # noqa: BLE001 — one page never aborts the others
                report.failed.append((source_name, str(e)))
                continue
            taken.add(target_name.casefold())
            if item_id is not None:
                report.overwritten.append(target_name)
            else:
                report.copied.append(target_name)
            if target_name != source_name:
                report.renamed.append((source_name, target_name))
            if page.published:
                report.published.append(target_name)
            if page.web_parts:
                report.web_part_pages.append(target_name)
            written[target_name] = page.canvas
        _verify(report, target_list, written)
    if report.failed:
        notes.append(
            f"page copy: {len(report.failed)} page(s) could not be copied: {_shown([name for name, _ in report.failed])}"
        )
    if report.mismatched:
        notes.append(
            f"page copy: {len(report.mismatched)} page(s) did not read back their canvas: {_shown(report.mismatched)}"
        )
    if report.web_part_pages:
        notes.append(
            f"page copy: {len(report.web_part_pages)} page(s) serialize client-side web parts whose data "
            f"bindings (list/library identifiers) are not remapped: {_shown(report.web_part_pages)}"
        )
    return report


def verify_page_copy(source_web: "Web", target_web: "Web") -> list[str]:
    """Notes for the modern pages a copy did not deliver (read-only).

    A source page counts as delivered when the target holds a page of the same
    name, or a page whose canvas is identical (the copy renames around an existing
    page). Only same-named pages are compared for drift, because a renamed copy is
    a different page by design.

    Args:
        source_web: The web the pages were captured from.
        target_web: The web the pages should have landed on.
    """
    source_pages = [
        page
        for sp_list in _page_libraries(source_web.lists.get().execute_query())
        for page in capture_site_pages(sp_list)
    ]
    if not source_pages:
        return []
    target_canvases: dict = {}
    for sp_list in _page_libraries(target_web.lists.get().execute_query()):
        items = sp_list.items.select(["FileLeafRef", "CanvasContent1"]).get().execute_query()
        for item in items:
            properties = item.properties
            target_canvases[str(properties.get("FileLeafRef") or "").casefold()] = properties.get("CanvasContent1")
    delivered = set(target_canvases.values())
    missing = [
        page.name
        for page in source_pages
        if page.name.casefold() not in target_canvases and page.canvas not in delivered
    ]
    drifted = [
        page.name
        for page in source_pages
        if page.name.casefold() in target_canvases and target_canvases[page.name.casefold()] != page.canvas
    ]
    notes = []
    if missing:
        notes.append(f"{len(missing)} modern page(s) have no target counterpart: {_shown(missing)}")
    if drifted:
        notes.append(f"{len(drifted)} page(s) differ from the source: {_shown(drifted)}")
    return notes


def _page_info(item: "ListItem") -> Optional[PageInfo]:
    properties = item.properties
    name = properties.get("FileLeafRef") or ""
    if not name.lower().endswith(".aspx"):
        return None
    canvas = properties.get("CanvasContent1") or ""
    wiki = properties.get("WikiField") or ""
    if is_modern_page(properties.get("ContentTypeId"), canvas):
        kind = "modern"
    else:
        kind = "classic" if wiki else "unknown"
    return PageInfo(name=name, kind=kind, web_parts=count_web_parts(canvas))


def _detect_library(sp_list: "SPList") -> Optional[PageLibrary]:
    if not _is_page_library(sp_list):
        return None
    items = sp_list.items.select(list(_DETECT_SELECT)).get().execute_query()
    pages = [page for page in (_page_info(item) for item in items) if page is not None]
    return PageLibrary(title=str(sp_list.title), pages=pages) if pages else None


def detect_page_handoff(lists: Iterable["SPList"]) -> PageHandoff:
    """Find the page libraries (and pages) a whole-site migration touches.

    ``lists`` is the source web's list collection (already loaded by the resolver),
    so no extra web query is issued. Read-only.
    """
    return PageHandoff(libraries=[library for library in (_detect_library(sp) for sp in lists) if library is not None])


def page_handoff_note(handoff: PageHandoff, *, modern_copied: bool = False) -> Optional[str]:
    """A one-line note for the pages a migration does not carry, or ``None``.

    Pass ``modern_copied`` once the modern pages were copied: the note then names
    only the classic pages, which need page transformation rather than a copy.
    """
    details = []
    for library in handoff.libraries:
        pages = library.classic_pages if modern_copied else library.pages
        if not pages:
            continue
        names = ", ".join(page.name for page in pages[:_MAX_PAGES_IN_NOTE])
        if len(pages) > _MAX_PAGES_IN_NOTE:
            names += f", +{len(pages) - _MAX_PAGES_IN_NOTE} more"
        summary = f"{library.title} ({len(pages)} page(s): {names})"
        if any(page.web_parts for page in pages):
            summary += f" with {sum(page.web_parts for page in pages)} web part(s)"
        details.append(summary)
    if not details:
        return None
    subject = (
        "classic page(s) are not migrated (they need page transformation)" if modern_copied else "pages are not migrated"
    )
    return f"{subject} — remediate out of band: " + "; ".join(details)


__all__ = [
    "DUPLICATE_OVERWRITE",
    "DUPLICATE_RENAME",
    "DUPLICATE_SKIP",
    "PAGE_LIBRARY_TEMPLATE",
    "SITE_PAGE_CONTENT_TYPE_PREFIX",
    "PageCopyReport",
    "PageHandoff",
    "PageInfo",
    "PageLibrary",
    "PagePayload",
    "apply_page_payload",
    "capture_page",
    "capture_site_pages",
    "copy_site_pages",
    "detect_page_handoff",
    "is_modern_page",
    "page_handoff_note",
    "verify_page_copy",
]
