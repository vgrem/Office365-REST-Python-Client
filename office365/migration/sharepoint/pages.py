"""Copy modern and classic wiki pages, and detect the pages a client-side copy skips.

A page library (``base_template`` 119 — *Site Pages*, wiki or publishing pages)
holds ``.aspx`` pages rather than documents, so the item adapters do not migrate
it. **Modern** site pages are still reachable over REST, so this module copies
them: the page is created through the ``sitepages`` endpoint, its canvas and page
metadata are written onto the created item, and the page is published when the
source page was published. What a copy cannot fix is the *inside* of a web part —
a serialized client-side web part keeps the source list/library identifiers it
binds to, and those are not remapped.

**Classic wiki** pages carry their body in ``WikiField`` instead of a canvas, and
that field is readable and writable over REST, so a wiki page is copied too: the
page is created in the target page library and the source ``WikiField`` value is
written back verbatim. **Publishing** pages and pages with neither a canvas nor a
wiki body stay transformation work, not copy work: :func:`detect_page_handoff`
inventories them and :func:`page_handoff_note` names them, so a run never
silently drops them.

Two facts this module relies on, both live-verified on a SharePoint Online tenant:

* ``POST /_api/sitepages/pages`` (``Web.add_site_page``) creates a modern page; a
  page created that way is a *draft* until
  ``POST /_api/sitepages/pages(<id>)/publish`` (``SitePage.publish``) runs, and a
  MERGE of ``OData__ModerationStatus`` does **not** publish it;
* a page's ``CanvasContent1`` round-trips byte-identical through
  ``item.set_property("CanvasContent1", ...)`` + ``item.update()``; a *newly
  created* page already carries a default empty canvas, which a MERGE of ``""``
  does not clear, so an empty source canvas is left alone and not verified;
* a wiki page is created with ``List.create_wiki_page(name, body)``, which the
  server normalizes once (it wraps the body in a ``ExternalClass`` div and
  entity-encodes braces); writing the *already normalized* source ``WikiField``
  value back round-trips byte-identical, so a copy reuses the source value
  instead of re-authoring the body;
* a created wiki page is a draft (``Level`` 2, status 3), and
  ``item.file.publish(comment)`` — not a moderation-status MERGE — publishes it;
* a web's home page designation is reachable as ``WelcomePage``, but a MERGE of it
  **on the web is silently ignored** — the write that takes effect goes to the
  root folder (``Folder.update()`` on ``/_api/web/rootfolder``), which is what
  :func:`apply_home_page` does.

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
    "WikiField",
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
    #: A classic wiki page's body (``WikiField``) — what it carries instead of a canvas.
    wiki: Optional[str] = None
    banner_image_url: Optional[dict] = None
    promoted_state: Optional[int] = None
    #: Whether the source page was published (approved), so the copy should publish too.
    published: bool = True
    #: Client-side web parts serialized in the canvas (their bindings are not remapped).
    web_parts: int = 0

    @property
    def is_classic(self) -> bool:
        """Whether this is a classic wiki page (a ``WikiField`` body, no canvas)."""
        return bool(self.wiki) and not is_modern_page(self.content_type_id, self.canvas)

    @property
    def content(self) -> Optional[str]:
        """The field value that carries the page body — what a copy writes and verifies."""
        return self.wiki if self.is_classic else self.canvas

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "title": self.title,
            "description": self.description,
            "promoted_state": self.promoted_state,
            "published": self.published,
            "web_parts": self.web_parts,
            "canvas_length": len(self.canvas or ""),
            "wiki_length": len(self.wiki or ""),
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
        """Wiki pages: a copy carries their ``WikiField`` body."""
        return [page for page in self.pages if page.kind == "classic"]

    @property
    def uncopyable_pages(self) -> list[PageInfo]:
        """Pages with neither a canvas nor a wiki body (publishing or blank pages)."""
        return [page for page in self.pages if page.kind == "unknown"]


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
    def uncopyable_page_count(self) -> int:
        return sum(len(library.uncopyable_pages) for library in self.libraries)

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
    #: Pages already present on the target with the source's own body (a re-run).
    unchanged: list[str] = field(default_factory=list)
    #: Pages published after their content was written.
    published: list[str] = field(default_factory=list)
    #: Pages whose canvas did not read back identical after the write.
    mismatched: list[str] = field(default_factory=list)
    #: ``(page name, error)`` for pages that could not be copied.
    failed: list[tuple[str, str]] = field(default_factory=list)
    #: Pages with neither a canvas nor a wiki body, left for page transformation.
    classic: list[str] = field(default_factory=list)
    #: Pages whose canvas serializes client-side web parts (bindings not remapped).
    web_part_pages: list[str] = field(default_factory=list)
    #: Classic wiki pages copied through their ``WikiField`` body.
    wiki: list[str] = field(default_factory=list)
    #: The target web-relative path the source's home page was copied to, if any.
    home_page: Optional[str] = None

    @property
    def page_count(self) -> int:
        return len(self.copied) + len(self.overwritten)

    @property
    def is_empty(self) -> bool:
        return self.page_count == 0

    def summary(self) -> Optional[str]:
        """One line describing what the copy did, or ``None`` when nothing happened."""
        if not self.copied and not self.overwritten and not self.skipped and not self.unchanged:
            return None
        parts = []
        if self.copied:
            detail = f"{len(self.copied)} page(s) copied"
            if self.wiki:
                detail += f" ({len(self.wiki)} classic wiki)"
            if self.renamed:
                detail += f" ({len(self.renamed)} renamed around an existing page)"
            parts.append(detail)
        if self.overwritten:
            parts.append(f"{len(self.overwritten)} overwritten")
        if self.skipped:
            parts.append(f"{len(self.skipped)} left as they were")
        if self.unchanged:
            parts.append(f"{len(self.unchanged)} already copied")
        if self.published:
            parts.append(f"{len(self.published)} published")
        if self.home_page:
            parts.append(f"home page is now {self.home_page}")
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
        wiki=properties.get("WikiField"),
        banner_image_url=properties.get("BannerImageUrl"),
        promoted_state=properties.get("PromotedState"),
        published=status in (None, 0, "0"),
        web_parts=count_web_parts(properties.get("CanvasContent1")),
    )


def capture_page(item: "ListItem") -> Optional[PagePayload]:
    """The payload of a copyable page item (modern or classic wiki), or ``None``."""
    properties = item.properties
    name = properties.get("FileLeafRef") or ""
    if not name.lower().endswith(".aspx"):
        return None
    if is_modern_page(properties.get("ContentTypeId"), properties.get("CanvasContent1")):
        return _payload(properties)
    payload = _payload(properties)
    return payload if payload.is_classic else None


def _classify(sp_list: "SPList") -> tuple[list[PagePayload], list[str]]:
    """Read one page library once: (copyable payloads, page names with no copyable body)."""
    payloads: list[PagePayload] = []
    classic: list[str] = []
    items = sp_list.items.select(list(_PAGE_SELECT)).get().execute_query()
    for item in items:
        properties = item.properties
        name = str(properties.get("FileLeafRef") or "")
        if not name.lower().endswith(".aspx"):
            continue
        payload = _payload(properties)
        if is_modern_page(properties.get("ContentTypeId"), properties.get("CanvasContent1")) or payload.is_classic:
            payloads.append(payload)
        else:
            classic.append(name)
    return payloads, classic


def capture_site_pages(sp_list: "SPList") -> list[PagePayload]:
    """The copyable pages of a page library (one projected read; read-only)."""
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


def _already_copied(page: "PagePayload", bodies: dict, consumed: set) -> Optional[str]:
    """The target page that already carries this page's body, if any.

    A copy writes the source body verbatim, so the body is the copy's identity. A
    second run over the same source and target therefore finds its own earlier copy
    — possibly renamed around an existing page — instead of minting ``Home-2.aspx``,
    ``Home-3.aspx``, ... on every run. The page of the same name is tried first (a
    page that kept its name costs one dict lookup); a body match elsewhere picks up
    the renamed copy. ``consumed`` makes each target page account for at most one
    source page, so two source pages with an identical body stay two copies.

    An empty body counts as a body: the server gives a created page an empty canvas
    of its own (``<div></div>``), which a copy never writes over, so a page with no
    canvas would otherwise be copied again on every run.
    """
    content = page.content or ""
    name = page.name.casefold()
    if name not in consumed and bodies.get(name) == content:
        return name
    return next(
        (candidate for candidate, body in bodies.items() if candidate not in consumed and body == content),
        None,
    )


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


def _copy_wiki_page(
    target_web: "Web",
    target_list: "SPList",
    page: PagePayload,
    target_name: str,
    item_id: Optional[int],
) -> None:
    """Create or overwrite a classic wiki page, then publish it when the source was.

    The body goes in through ``create_wiki_page`` (an existing page is rewritten with
    a ``WikiField`` MERGE), and publishing runs through ``item.file.publish``: a
    moderation-status MERGE does not publish a classic page.
    """
    body = page.wiki
    if not body:
        raise ValueError(f"classic page {target_name!r} carries no wiki body")
    if item_id is None:
        created = target_list.create_wiki_page(target_name, body).execute_query()
        item_id = created.list_item_all_fields.select(["Id"]).get().execute_query().properties.get("Id")
        if item_id is None:
            raise ValueError(f"the target did not return an id for the created page {target_name!r}")
    item = target_list.get_item_by_id(item_id)
    values = {"WikiField": body, "Title": page.title, "Description": page.description}
    for name, value in values.items():
        if value is not None:
            item.set_property(name, value)
    item.update()
    target_web.context.execute_query()
    if page.published:
        item.file.publish("").execute_query()


def _copy_page(
    target_web: "Web",
    target_list: "SPList",
    page: PagePayload,
    target_name: str,
    item_id: Optional[int],
) -> None:
    """Create or overwrite one page and publish it when the source page was."""
    if page.is_classic:
        _copy_wiki_page(target_web, target_list, page, target_name, item_id)
        return
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
    """Read the copied pages back once and compare the field that carries their body."""
    if not written:
        return
    items = target_list.items.select(["FileLeafRef", "CanvasContent1", "WikiField"]).get().execute_query()
    written_back = {
        str(item.properties.get("FileLeafRef") or "").casefold(): (
            item.properties.get("CanvasContent1"),
            item.properties.get("WikiField"),
        )
        for item in items
    }
    for name, (index, expected) in written.items():
        if not expected:
            continue
        if written_back.get(name.casefold(), (None, None))[index] != expected:
            report.mismatched.append(name)


def _copy_library(
    target_web: "Web", target_list: "SPList", payloads: list, behavior: str, report: "PageCopyReport"
) -> None:
    """Copy one page library's payloads onto the target, then read the bodies back."""
    existing: dict = {}
    bodies: dict = {}
    names: dict = {}
    for item in target_list.items.select(["Id", "FileLeafRef", "CanvasContent1", "WikiField"]).get().execute_query():
        name = str(item.properties.get("FileLeafRef") or "").casefold()
        existing[name] = item.properties.get("Id")
        names[name] = str(item.properties.get("FileLeafRef") or "")
        bodies[name] = _body(item.properties) or ""
    taken = set(existing)
    consumed: set = set()
    written: dict = {}
    for page in payloads:
        if behavior == DUPLICATE_RENAME:
            matched = _already_copied(page, bodies, consumed)
            if matched is not None:
                consumed.add(matched)
                report.unchanged.append(page.name)
                if matched != page.name.casefold():
                    report.renamed.append((page.name, names.get(matched, matched)))
                continue
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
        consumed.add(target_name.casefold())
        bodies[target_name.casefold()] = page.content or ""
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
        if page.is_classic:
            report.wiki.append(target_name)
            written[target_name] = (1, page.wiki)
        else:
            written[target_name] = (0, page.canvas)
    _verify(report, target_list, written)


def copy_site_pages(
    source_web: "Web",
    target_web: "Web",
    *,
    duplicate_behavior: str = DUPLICATE_RENAME,
    warnings: Optional[list[str]] = None,
) -> PageCopyReport:
    """Copy the source web's modern and classic wiki pages to the target web's page library.

    Read the source page libraries once each, create (or overwrite) the pages on
    the target, write the canvas and page metadata, publish the pages the source
    had published, and read the bodies back to verify the write. Modern pages are
    created through the ``sitepages`` endpoint, classic wiki pages through
    ``create_wiki_page`` (their ``WikiField`` body is carried verbatim); a page with
    neither a canvas nor a wiki body is reported in :attr:`PageCopyReport.classic`
    because copying cannot transform it.

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
        _copy_library(target_web, target_list, payloads, behavior, report)
    notes.extend(_gap_notes(report))
    report.home_page = apply_home_page(source_web, target_web, renamed=dict(report.renamed), warnings=notes)
    return report


def _gap_notes(report: "PageCopyReport") -> list[str]:
    """One note per way the copy fell short of a byte-identical page."""
    notes = []
    if report.failed:
        notes.append(
            f"page copy: {len(report.failed)} page(s) could not be copied: {_shown([name for name, _ in report.failed])}"
        )
    if report.mismatched:
        notes.append(
            f"page copy: {len(report.mismatched)} page(s) did not read back their canvas: {_shown(report.mismatched)}"
        )
    if report.wiki:
        notes.append(
            f"page copy: {len(report.wiki)} classic wiki page(s) were copied verbatim — wiki markup "
            f"(internal links, embedded web parts) is not rewritten: {_shown(report.wiki)}"
        )
    if report.web_part_pages:
        notes.append(
            f"page copy: {len(report.web_part_pages)} page(s) serialize client-side web parts whose data "
            f"bindings (list/library identifiers) are not remapped: {_shown(report.web_part_pages)}"
        )
    return notes


def capture_home_page(web: "Web") -> Optional[str]:
    """A web's home page as a web-relative path (``SitePages/Home.aspx``), or ``None`` (read-only)."""
    web = web.select(["WelcomePage"]).get().execute_query()
    return web.properties.get("WelcomePage") or None


def _page_name(path: Optional[str]) -> str:
    """The case-folded file name of a web-relative page path."""
    return (path or "").rsplit("/", 1)[-1].casefold()


def _target_refs(target_web: "Web") -> dict:
    """``file name -> FileRef`` for every page in the target's page libraries (one read each)."""
    return {
        _page_name(str(item.properties.get("FileLeafRef") or "")): str(item.properties.get("FileRef") or "")
        for sp_list in _page_libraries(target_web.lists.get().execute_query())
        for item in sp_list.items.select(["FileLeafRef", "FileRef"]).get().execute_query()
    }


def apply_home_page(
    source_web: "Web",
    target_web: "Web",
    *,
    renamed: Optional[dict] = None,
    warnings: Optional[list[str]] = None,
) -> Optional[str]:
    """Point the target web's home page at the copy of the source web's home page.

    A migrated site that opens on a different page than its source is not migrated,
    and nothing else in a copy moves the home page designation. The source's
    ``WelcomePage`` is resolved through the copy's renames (a page copied as
    ``Home-1.aspx`` becomes the home page), then written onto the target's *root
    folder* — a MERGE of ``WelcomePage`` on the web itself is silently ignored.
    Nothing is written when the target already matches.

    Args:
        source_web: The web whose home page is the reference (read-only).
        target_web: The web that should open on the copy.
        renamed: ``{source name: target name}`` pairs from the copy (any case).
        warnings: Collected notes; a home page that was not copied is appended here.

    Returns:
        The target web-relative path written, or ``None`` when nothing was written.
    """
    source_path = capture_home_page(source_web)
    if not source_path:
        return None
    notes = warnings if warnings is not None else []
    mapping = {_page_name(source): target for source, target in (renamed or {}).items()}
    target_name = mapping.get(_page_name(source_path), _page_name(source_path))
    ref = _target_refs(target_web).get(_page_name(target_name))
    if not ref:
        notes.append(
            f"page copy: the source web's home page '{source_path}' was not copied — the target keeps its own home page"
        )
        return None
    folder = target_web.root_folder.select(["ServerRelativeUrl", "WelcomePage"]).get().execute_query()
    origin = str(folder.properties.get("ServerRelativeUrl") or "")
    path = ref[len(origin) :].lstrip("/") if origin and ref.lower().startswith(origin.lower()) else ref.lstrip("/")
    if folder.properties.get("WelcomePage") == path:
        return None
    folder.set_property("WelcomePage", path)
    folder.update()
    target_web.context.execute_query()
    return path


def _home_page_notes(source_web: "Web", target_web: "Web", source_pages: list, target_bodies: dict) -> list[str]:
    """Notes for a target whose home page is not the copy of the source's (read-only)."""
    source_path = capture_home_page(source_web)
    source_page = next((page for page in source_pages if page.name.casefold() == _page_name(source_path)), None)
    if source_page is None:
        return []
    target_path = capture_home_page(target_web)
    if target_bodies.get(_page_name(target_path)) == (source_page.content or ""):
        return []
    return [
        f"the target's home page is '{target_path or ''}', not the copy of '{source_path}' — "
        f"a migrated site opens on the wrong page"
    ]


def verify_page_copy(source_web: "Web", target_web: "Web") -> list[str]:
    """Notes for the pages a copy did not deliver (read-only).

    A source page counts as delivered when the target holds a page of the same
    name, or a page whose body is identical (the copy renames around an existing
    page). A same-named target page is only compared for drift when the source body
    is nowhere on the target — otherwise the copy landed under a renamed name and the
    same-named page is simply the target's own page.

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
    target_bodies: dict = {}
    for sp_list in _page_libraries(target_web.lists.get().execute_query()):
        items = sp_list.items.select(["FileLeafRef", "CanvasContent1", "WikiField"]).get().execute_query()
        for item in items:
            properties = item.properties
            target_bodies[str(properties.get("FileLeafRef") or "").casefold()] = _body(properties) or ""
    delivered = set(target_bodies.values())
    missing = [
        page.name
        for page in source_pages
        if page.name.casefold() not in target_bodies and (page.content or "") not in delivered
    ]
    drifted = [
        page.name
        for page in source_pages
        if page.name.casefold() in target_bodies
        and target_bodies[page.name.casefold()] != (page.content or "")
        and (page.content or "") not in delivered
    ]
    notes = []
    if missing:
        notes.append(f"{len(missing)} page(s) have no target counterpart: {_shown(missing)}")
    if drifted:
        notes.append(f"{len(drifted)} page(s) differ from the source: {_shown(drifted)}")
    notes.extend(_home_page_notes(source_web, target_web, source_pages, target_bodies))
    return notes


def _body(properties: dict) -> Optional[str]:
    """The body a target page item carries — its canvas, or a wiki page's ``WikiField``."""
    canvas = properties.get("CanvasContent1")
    return canvas or properties.get("WikiField")


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

    Pass ``modern_copied`` once the modern and classic wiki pages were copied: the
    note then names only the pages with no copyable body, which need page
    transformation rather than a copy.
    """
    details = []
    for library in handoff.libraries:
        pages = library.uncopyable_pages if modern_copied else library.pages
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
        "page(s) are not migrated (no modern canvas, no wiki body — they need page transformation)"
        if modern_copied
        else "pages are not migrated"
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
    "apply_home_page",
    "apply_page_payload",
    "capture_home_page",
    "capture_page",
    "capture_site_pages",
    "copy_site_pages",
    "detect_page_handoff",
    "is_modern_page",
    "page_handoff_note",
    "verify_page_copy",
]
