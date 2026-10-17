"""Detect pages (and the web parts they carry) that a whole-site migration skips.

A page library (``base_template`` 119 — *Site Pages*, wiki or publishing pages)
holds ``.aspx`` pages, not documents, so the item adapters deliberately do not
migrate it: page transformation belongs to external tools (PnP), not here. To
keep the gap honest, the whole-site resolver calls :func:`detect_page_handoff`
and appends the human-readable :func:`page_handoff_note` to its warnings, so a
run never silently drops a site's pages.

Detection is read-only and verifiable: it names the page libraries, their pages,
and how many client-side web parts a modern page serializes in its canvas (the
canvas itself is parsed by
:func:`office365.sharepoint.publishing.pages.canvas.parse_canvas_controls`).

:mod:`office365.migration.sharepoint.handoff` composes this module with the other
uncopyable artifacts (workflows, InfoPath forms, BCS external lists) and is what
the whole-site resolver actually calls.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Iterable, Optional

from office365.sharepoint.lists.templates.type import ListTemplateType
from office365.sharepoint.publishing.pages.canvas import count_web_parts

if TYPE_CHECKING:
    from office365.sharepoint.listitems.listitem import ListItem
    from office365.sharepoint.lists.list import List as SPList

#: ``SPListTemplateType.WebPageLibrary`` — Site Pages, wiki and publishing pages.
PAGE_LIBRARY_TEMPLATE = ListTemplateType.WebPageLibrary.value

#: Page names shown inline in the handoff note before it is truncated.
_MAX_PAGES_IN_NOTE = 5


@dataclass
class PageInfo:
    """One page in a skipped page library."""

    name: str
    kind: str  #: ``modern`` (has a canvas), ``classic`` (WikiField) or ``unknown``
    web_parts: int = 0


@dataclass
class PageLibrary:
    """A page library that the migration skips, with the pages it holds."""

    title: str
    pages: list[PageInfo] = field(default_factory=list)

    @property
    def web_part_count(self) -> int:
        return sum(page.web_parts for page in self.pages)


@dataclass
class PageHandoff:
    """Everything a whole-site migration leaves for out-of-band remediation."""

    libraries: list[PageLibrary] = field(default_factory=list)

    @property
    def page_count(self) -> int:
        return sum(len(library.pages) for library in self.libraries)

    @property
    def web_part_count(self) -> int:
        return sum(library.web_part_count for library in self.libraries)

    @property
    def is_empty(self) -> bool:
        return self.page_count == 0


def _page_info(item: ListItem) -> Optional[PageInfo]:
    properties = item.properties
    name = properties.get("FileLeafRef") or ""
    if not name.lower().endswith(".aspx"):
        return None
    canvas = properties.get("CanvasContent1") or ""
    wiki = properties.get("WikiField") or ""
    kind = "modern" if canvas else ("classic" if wiki else "unknown")
    return PageInfo(name=name, kind=kind, web_parts=count_web_parts(canvas))


def _detect_library(sp_list: SPList) -> Optional[PageLibrary]:
    title = sp_list.title
    if not title or sp_list.hidden:
        return None
    if sp_list.base_template != PAGE_LIBRARY_TEMPLATE:
        return None
    items = sp_list.items.get().select(["FileLeafRef", "CanvasContent1", "WikiField"]).execute_query()
    pages = [page for page in (_page_info(item) for item in items) if page is not None]
    return PageLibrary(title=title, pages=pages) if pages else None


def detect_page_handoff(lists: Iterable[SPList]) -> PageHandoff:
    """Find the page libraries (and pages) a whole-site migration would skip.

    ``lists`` is the source web's list collection (already loaded by the resolver),
    so no extra web query is issued. Read-only.
    """
    return PageHandoff(libraries=[library for library in (_detect_library(sp) for sp in lists) if library is not None])


def page_handoff_note(handoff: PageHandoff) -> Optional[str]:
    """A one-line handoff note for the skipped pages, or ``None`` when there are none."""
    if handoff.is_empty:
        return None
    details = []
    for library in handoff.libraries:
        names = ", ".join(page.name for page in library.pages[:_MAX_PAGES_IN_NOTE])
        if len(library.pages) > _MAX_PAGES_IN_NOTE:
            names += f", +{len(library.pages) - _MAX_PAGES_IN_NOTE} more"
        summary = f"{library.title} ({len(library.pages)} page(s): {names})"
        if library.web_part_count:
            summary += f" with {library.web_part_count} web part(s)"
        details.append(summary)
    return "pages/web parts are not migrated — remediate out of band: " + "; ".join(details)


__all__ = [
    "PAGE_LIBRARY_TEMPLATE",
    "PageHandoff",
    "PageInfo",
    "PageLibrary",
    "detect_page_handoff",
    "page_handoff_note",
]
