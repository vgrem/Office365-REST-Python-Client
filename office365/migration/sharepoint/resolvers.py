"""Resolve a declarative :class:`MigrationTask` into source/target adapters.

SPMT-shaped tasks (``Add-SPMTTask``) name a source and a target site/list; this
turns them into the toolkit's ``DataSource``/``DataTarget`` pair against a
SharePoint ``ClientContext``. Client-side REST uploads are the default; set
``MigrationSettings.use_migration_api`` for the server-side Migration API path
(full fidelity: versions/ACLs).

A **site** task (``migrate_all``) is resolved by :func:`resolve_site_task`, which
walks the source web's lists and document libraries and returns one adapter pair
per migratable list. The registered ``context`` is the target; a source on a
different site collection in the same tenant is reached through an authenticated
clone (:meth:`ClientContext.clone`).

Subsites are **not** migrated by default: they are detected and reported through
the resolution ``warnings`` sink (``session.warnings()``). Pass
``include_subwebs=True`` to provision the matching target subsites and migrate
their lists too. Every web is addressed through its own clone (a subweb's
sub-collections resolve against the context root otherwise).

The artifacts a client-side copy cannot carry — pages/web parts, workflow
associations, InfoPath forms and business-data (BCS) external lists — are
reported through the same sink (see
:mod:`office365.migration.sharepoint.handoff`).
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Callable, Iterable, Sequence, Union

from office365.migration.adapters.filesystem import FileSystemSource
from office365.migration.map import ContentTypeMap
from office365.migration.sharepoint.adapters import (
    SharePointLibrarySource,
    SharePointLibraryTarget,
    SharePointListSource,
    SharePointListTarget,
)
from office365.migration.sharepoint.branding import WebBrandingReport, apply_web_branding
from office365.migration.sharepoint.handoff import EXTERNAL_LIST_TEMPLATE, detect_handoff, handoff_notes
from office365.migration.sharepoint.navigation import apply_navigation
from office365.migration.sharepoint.pages import DUPLICATE_RENAME, PageCopyReport, copy_site_pages
from office365.migration.sharepoint.security import apply_site_security
from office365.migration.sharepoint.site_settings import WebSettingsReport, apply_web_settings
from office365.migration.sharepoint.structure import (
    capture_list_structure,
    compare_web_scope_structure,
    normalize_guid,
    provision_list_structure,
    provision_web_scope_columns,
    web_scope_note,
)
from office365.migration.tasks import FILE_SHARE, SHAREPOINT, MigrationTask
from office365.runtime.operations import Progress
from office365.sharepoint.lists.base_type import BaseType
from office365.sharepoint.lists.templates.type import ListTemplateType
from office365.sharepoint.webs.creation_information import WebCreationInformation

if TYPE_CHECKING:
    from office365.migration.settings import MigrationSettings
    from office365.migration.sharepoint.package_target import SharePointPackageTarget
    from office365.sharepoint.client_context import ClientContext
    from office365.sharepoint.folders.folder import Folder
    from office365.sharepoint.lists.list import List as SPList
    from office365.sharepoint.webs.web import Web

    #: The adapter pairs a resolver builds. A file-share source still targets a
    #: SharePoint list/library; only the server-side package path differs.
    Source = Union[FileSystemSource, SharePointLibrarySource, SharePointListSource]
    Target = Union[SharePointLibraryTarget, SharePointListTarget, SharePointPackageTarget]

logger = logging.getLogger(__name__)

__all__ = ["is_document_library", "is_migratable_list", "resolve_site_task", "resolve_task"]

#: SharePoint's own infrastructure templates (user information, catalogs,
#: workflow/translation plumbing) plus the Site Pages library, which needs
#: page-aware handling the generic adapters do not provide yet.
_SYSTEM_BASE_TEMPLATES = frozenset({112, 113, 114, 115, 116, 117, 118, 119, 121, 122, 123, 124, 125, 126, 127, 130})

#: ``SPBaseType.DocumentLibrary`` — libraries hold files; everything else is a
#: record list.
_DOCUMENT_LIBRARY = BaseType.DocumentLibrary.value


def is_document_library(sp_list: SPList) -> bool:
    """Whether a SharePoint list is a document library (holds files, not records)."""
    return sp_list.base_type == _DOCUMENT_LIBRARY


def is_migratable_list(sp_list: SPList) -> bool:
    """Whether a list/library takes part in a whole-site migration.

    Skips hidden lists, SharePoint infrastructure templates, and system lists
    that cannot be deleted (e.g. ``User Information``). A business-data (BCS)
    external list is skipped too: it is a view over a BDC model that a copy
    cannot provision, so :func:`~office365.migration.sharepoint.handoff.detect_handoff`
    reports it instead of the structure replay creating a hollow list.
    """
    if sp_list.hidden:
        return False
    if sp_list.allow_deletion is False:
        return False
    if sp_list.base_template == EXTERNAL_LIST_TEMPLATE:
        return False
    return sp_list.base_template not in _SYSTEM_BASE_TEMPLATES


def resolve_task(
    task: MigrationTask,
    context: ClientContext,
    settings: "MigrationSettings | None" = None,
    *,
    provision_structure: bool = True,
) -> tuple[Source, Target]:
    """Return a single ``(source, target)`` adapter pair for a task descriptor.

    Use :func:`resolve_site_task` for ``migrate_all`` / whole-site tasks. For a
    SharePoint task, the target list's structure is replayed from the source
    before content is copied (``provision_structure=False`` to skip that).
    """
    if task.kind == FILE_SHARE:
        return _file_share(task, context, settings)
    if task.kind == SHAREPOINT:
        if task.migrate_all or not task.source_list:
            raise NotImplementedError(
                "resolve_task resolves one source list; use resolve_site_task (or "
                "MigrationSession.add_site_task) for a whole-site / migrate_all task"
            )
        return _sharepoint(task, context, settings, provision_structure=provision_structure)
    raise ValueError(f"unsupported task kind {task.kind!r}")


def _report(
    progress: "Callable[[Progress], None] | None",
    done: int,
    total: int | None,
    stage: str,
    title: str | None = None,
) -> None:
    """Emit one resolution step, if a callback was supplied.

    Resolution used to be the session's silent phase: it provisions target
    containers and replays every list's structure before anything is copied, so a
    run printed its plan and then sat quiet. These steps give the same
    ``Progress`` heartbeat the runner emits, using its vocabulary: ``lists`` (what
    is in scope), ``containers`` (target lists created/found), ``structure`` (per
    list columns/content types/views), and the indeterminate ``pages`` /
    ``navigation`` / ``branding`` stages.
    """
    if progress is not None:
        progress(Progress(done=done, total=total, stage=stage, items=[title] if title else None))


def resolve_site_task(
    task: MigrationTask,
    context: ClientContext,
    settings: "MigrationSettings | None" = None,
    *,
    include: Sequence[str] | None = None,
    exclude: Sequence[str] | None = None,
    provision_structure: bool = True,
    include_subwebs: bool = False,
    preserve_permissions: bool = False,
    migrate_navigation: bool = False,
    migrate_pages: bool = True,
    duplicate_page_behavior: str = DUPLICATE_RENAME,
    migrate_site_settings: bool = True,
    warnings: list[str] | None = None,
    progress: "Callable[[Progress], None] | None" = None,
) -> list[tuple[Source, Target]]:
    """Resolve a whole-site task into one ``(source, target)`` pair per list.

    Walks every migratable list and document library on the source site, pairs it
    with the target list of the same title (**creating the list container if it is
    missing**), and, unless ``provision_structure`` is false, replays the source
    list's columns, content types and views onto the target before content is
    copied (:func:`~office365.migration.sharepoint.structure.provision_list_structure`).
    The registered ``context`` is treated as the target site; a source on a
    different site collection in the same tenant is reached through an
    authenticated clone.

    By default the source web's **subsites are not migrated**; when any exist a
    human-readable note is appended to ``warnings`` (and logged). Pass
    ``include_subwebs=True`` to mirror the subsite tree on the target (creating a
    missing target subsite with the source's template) and migrate their lists too.

    Args:
        task: A ``SHAREPOINT`` task; its ``source_list`` is ignored.
        context: The target ``ClientContext``.
        settings: Migration settings (the server-side Migration API path is not
            supported for whole-site tasks).
        include: If given, only these source list titles are migrated.
        exclude: Source list titles to skip.
        provision_structure: Recreate the source list's structure on the target
            list (default). Pass ``False`` to only create the containers.
        include_subwebs: Recurse into subsites, creating matching target subsites.
        preserve_permissions: Best-effort re-create each web's security scope —
            custom site groups, their membership, and web-level role assignments
            (same-tenant, by login). Unresolvable principals are reported.
        migrate_navigation: Best-effort copy each web's Quick Launch and top
            navigation (source links rewritten to the target). Additive and
            idempotent; dynamic nodes are skipped.
        migrate_pages: Copy each web's modern site pages — the page is created
            through the ``sitepages`` endpoint, its canvas and page metadata are
            written, and it is published when the source page was. Classic pages
            and web part data bindings are reported, not carried.
        duplicate_page_behavior: What to do when a target page of that name
            already exists — ``RENAME`` (default, as SPMT), ``SKIP`` or
            ``OVERWRITE``.
        migrate_site_settings: Copy each web's ``Title`` and ``Description`` onto
            the target web when they differ (the ``PRESERVE_ALL_SETTINGS`` mode),
            and carry its branding (master page, custom master, logo, alternate CSS
            and theme folder) rebased onto the target's path, written only where the
            target resolves the asset it names. The site-collection and regional
            settings stay out of scope and are reported.
        warnings: Optional sink for resolution-level notes (subsites skipped,
            web parts, workflows, InfoPath forms, BCS external lists and pages with
            no copyable body detected but not migrated).
        progress: Optional ``ProgressCallback`` fired as containers are created and
            each list's structure is replayed, so the provisioning phase reports
            instead of running silent (``lists`` / ``containers`` / ``structure``
            stages, then indeterminate ``pages`` / ``navigation`` / ``branding``
            ones).
    """
    if task.kind != SHAREPOINT:
        raise ValueError(f"a site task must be kind {SHAREPOINT!r}, got {task.kind!r}")
    if settings is not None and settings.use_migration_api:
        raise NotImplementedError(
            "the server-side Migration API target is per-library; register one task "
            "per library instead of a whole-site task"
        )
    source_context = _context_for(context, task.sharepoint_source_site_url)
    target_context = _context_for(context, task.target_site_url)
    include_titles = set(include) if include else None
    exclude_titles = set(exclude) if exclude else set()

    pairs: list[tuple[Source, Target]] = []
    _resolve_web(
        source_context,
        target_context,
        include_titles,
        exclude_titles,
        provision_structure,
        include_subwebs,
        preserve_permissions,
        migrate_navigation,
        migrate_pages,
        duplicate_page_behavior,
        migrate_site_settings,
        warnings if warnings is not None else [],
        pairs,
        progress=progress,
    )
    return pairs


def _report_pages(
    source_web: Web,
    target_web: Web,
    duplicate_behavior: str,
    warnings: list[str],
    progress: "Callable[[Progress], None] | None" = None,
) -> PageCopyReport | None:
    """Copy the web's modern site pages, reporting what a copy cannot carry."""
    _report(progress, 0, None, "pages")
    try:
        report = copy_site_pages(source_web, target_web, duplicate_behavior=duplicate_behavior, warnings=warnings)
    except Exception as e:  # noqa: BLE001 — page copy is best-effort; never abort resolution
        warnings.append(f"page copy failed for {_web_url(source_web)}: {e}")
        return None
    summary = report.summary()
    if summary:
        logger.info(summary)
        warnings.append(summary)
    return report


def _report_handoff(
    source_web: Web,
    source_lists: Iterable[SPList],
    warnings: list[str],
    page_report: PageCopyReport | None = None,
) -> None:
    """Append handoff notes for the artifacts the adapters cannot carry (best-effort)."""
    try:
        notes = handoff_notes(detect_handoff(source_web, source_lists), page_report)
    except Exception as e:  # noqa: BLE001 — handoff detection is best-effort; never abort resolution
        warnings.append(f"handoff detection failed for {_web_url(source_web)}: {e}")
        return
    warnings.extend(notes)


def _apply_web_settings(
    source_web: Web, target_web: Web, preserve: bool, warnings: list[str]
) -> WebSettingsReport | None:
    """Copy the web's Title/Description, reporting what a copy cannot carry."""
    try:
        report = apply_web_settings(source_web, target_web, preserve=preserve)
    except Exception as e:  # noqa: BLE001 — site settings are best-effort; never abort resolution
        warnings.append(f"site settings copy failed for {_web_url(target_web)}: {e}")
        return None
    note = report.summary()
    if note:
        warnings.append(note)
    return report


def _apply_web_branding(
    source_web: Web, target_web: Web, preserve: bool, warnings: list[str]
) -> WebBrandingReport | None:
    """Copy the web's branding, reporting the assets the target does not have."""
    try:
        report = apply_web_branding(source_web, target_web, preserve=preserve)
    except Exception as e:  # noqa: BLE001 — branding is best-effort; never abort resolution
        warnings.append(f"branding copy failed for {_web_url(target_web)}: {e}")
        return None
    note = report.summary()
    if note:
        warnings.append(note)
    return report


def _provision_web_scope_structure(
    source_web: Web,
    target_web: Web,
    enable: bool,
    list_id_map: dict[str, str] | None,
    warnings: list[str],
) -> None:
    """Register the web's own site columns before the per-list replay (best-effort)."""
    if not enable:
        return
    try:
        report = provision_web_scope_columns(source_web, target_web, list_id_map=list_id_map)
    except Exception as e:  # noqa: BLE001 — web-scope provisioning is best-effort; never abort resolution
        warnings.append(f"web-scope column provisioning failed for {_web_url(target_web)}: {e}")
        return
    summary = report.summary()
    if summary:
        logger.info(summary)
        warnings.append(summary)
    warnings.extend(report.warnings())


def _report_web_scope_structure(source_web: Web, target_web: Web, warnings: list[str]) -> None:
    """Append a note naming the web-scope structure the target web lacks (best-effort)."""
    try:
        missing = compare_web_scope_structure(source_web, target_web)
    except Exception as e:  # noqa: BLE001 — comparison is best-effort; never abort resolution
        warnings.append(f"web-scope structure comparison failed for {_web_url(target_web)}: {e}")
        return
    note = web_scope_note(missing, _web_url(source_web))
    if note:
        logger.debug(note)
        warnings.append(note)


def _resolve_web(
    source_context: ClientContext,
    target_context: ClientContext,
    include_titles: set[str] | None,
    exclude_titles: set[str],
    provision_structure: bool,
    include_subwebs: bool,
    preserve_permissions: bool,
    migrate_navigation: bool,
    migrate_pages: bool,
    duplicate_page_behavior: str,
    preserve_site_settings: bool,
    warnings: list[str],
    pairs: list[tuple[Source, Target]],
    *,
    progress: "Callable[[Progress], None] | None" = None,
) -> None:
    """Resolve one web's lists, then recurse into its subsites when requested."""
    if preserve_permissions:
        try:
            apply_site_security(source_context.web, target_context.web, warnings)
        except Exception as e:  # noqa: BLE001 — site security is best-effort; never abort list resolution
            warnings.append(f"site security replication failed for {_web_url(source_context.web)}: {e}")
    if migrate_navigation:
        _report(progress, 0, None, "navigation")
        try:
            apply_navigation(source_context.web, target_context.web, warnings)
        except Exception as e:  # noqa: BLE001 — navigation is best-effort; never abort list resolution
            warnings.append(f"navigation replication failed for {_web_url(source_context.web)}: {e}")
    _apply_web_settings(source_context.web, target_context.web, preserve_site_settings, warnings)
    _report(progress, 0, None, "lists")
    source_lists: Iterable[SPList] = source_context.web.lists.get().execute_query()
    # Modern and classic wiki pages are copied; web part data bindings, wiki markup
    # that addresses the source site, workflows, InfoPath forms, BCS external lists
    # and pages with no copyable body are outside what a client-side copy can carry —
    # report them rather than dropping them silently.
    page_report = (
        _report_pages(source_context.web, target_context.web, duplicate_page_behavior, warnings, progress)
        if migrate_pages
        else None
    )
    _report_handoff(source_context.web, source_lists, warnings, page_report)
    selected = _select_lists(source_lists, include_titles, exclude_titles)
    _report(progress, 0, len(selected), "containers")

    # Create/resolve every target container *before* replaying any structure: a
    # lookup column names the list it points at, so that list must already exist
    # (and have a known target id) when the referencing list's fields are replayed.
    resolved = []
    for position, source_list in enumerate(selected, start=1):
        resolved.append((source_list, _ensure_target_list(target_context, source_list)))
        _report(progress, position, len(selected), "containers", source_list.title)
    list_id_map = _list_id_map_from_pairs(resolved)
    # A lookup may reference a list that is *not* in the include/exclude scope but
    # is already present on the target; match those by title so their values can
    # still be remapped instead of being dropped.
    targets_by_title = _target_list_ids_by_title(target_context.web)
    for source_list in source_lists:
        source_id = normalize_guid(source_list.id)
        title = source_list.title
        target_id = targets_by_title.get(title) if title else None
        if source_id and target_id and source_id not in list_id_map:
            list_id_map[source_id] = target_id

    # The web's own site columns are registered *before* any list is replayed: a
    # list's Fields collection includes the site columns it inherits, so a replayed
    # list then uses the web column instead of minting a second, list-scoped copy.
    # Afterwards, say which web-level definitions the target still lacks.
    _provision_web_scope_structure(source_context.web, target_context.web, provision_structure, list_id_map, warnings)
    _report_web_scope_structure(source_context.web, target_context.web, warnings)

    for position, (source_list, target_list) in enumerate(resolved, start=1):
        if provision_structure:
            content_type_map, structure_warnings = _provision_structure(source_list, target_list, list_id_map)
        else:
            content_type_map, structure_warnings = None, []
        source, target = _list_adapters(source_list, target_list, content_type_map=content_type_map)
        _attach_warnings(target, structure_warnings)
        pairs.append((source, target))
        _report(progress, position, len(resolved), "structure", source_list.title)

    # Branding last: an alternate-CSS URL may point into a library this run just
    # populated, so the asset has to exist before it is copied.
    _report(progress, 0, None, "branding")
    _apply_web_branding(source_context.web, target_context.web, preserve_site_settings, warnings)

    child_webs = list(source_context.web.webs.get().execute_query())
    if not child_webs:
        return
    if not include_subwebs:
        names = [web.title or _web_identity(web)[0] for web in child_webs]
        note = (
            f"{len(child_webs)} subsite(s) were not migrated (pass include_subwebs=True to "
            f"include them): {', '.join(names)}"
        )
        logger.debug(note)
        warnings.append(note)
        return
    for source_child in child_webs:
        target_child, target_child_context = _ensure_target_web(target_context, source_child)
        _resolve_web(
            _context_for(source_context, _web_url(source_child)),
            target_child_context,
            include_titles,
            exclude_titles,
            provision_structure,
            include_subwebs,
            preserve_permissions,
            migrate_navigation,
            migrate_pages,
            duplicate_page_behavior,
            preserve_site_settings,
            warnings,
            pairs,
            progress=progress,
        )


def _select_lists(
    source_lists: Iterable[SPList],
    include_titles: set[str] | None,
    exclude_titles: set[str],
) -> list[SPList]:
    """The lists a run migrates: migratable, and inside the include/exclude scope."""
    selected: list[SPList] = []
    for source_list in source_lists:
        title = source_list.title
        if not title or title in exclude_titles:
            continue
        if include_titles is not None and title not in include_titles:
            continue
        if not is_migratable_list(source_list):
            continue
        selected.append(source_list)
    return selected


def _provision_structure(
    source_list: SPList, target_list: SPList, list_id_map: dict[str, str] | None = None
) -> tuple[ContentTypeMap, list[str]]:
    """Capture the source list structure and replay it onto the target list.

    Structure provisioning is best-effort where SharePoint Online constrains it
    (a fresh column cannot be attached to a custom content type over REST); those
    columns are reported as warnings rather than aborting the resolution.

    Args:
        source_list: The source list whose structure is captured.
        target_list: The target list to replay it onto (container must exist).
        list_id_map: Normalized source list id -> target list id, used to repoint
            lookup columns at the target list (see
            :func:`~office365.migration.sharepoint.structure.rewrite_lookup_schema`).

    Returns:
        The content-type identity map built while provisioning (SharePoint
        assigns recreated list content types a fresh ``StringId``, so items
        carrying the source ``ContentTypeId`` must be rewritten to the target
        one) and the human-readable warnings the target did not apply.
    """
    structure = capture_list_structure(source_list)
    entries: dict[str, str] = {}
    warnings: list[str] = []
    for warning in provision_list_structure(target_list, structure, content_type_map=entries, list_id_map=list_id_map):
        # The list's name is the log line's context; the bare warning goes to the
        # caller's sink, which is where an operator already reads it. Logging it at
        # ``warning`` too printed every note twice (once with the prefix, once
        # without) through logging's last-resort handler.
        logger.debug("list %r: %s", source_list.title, warning)
        warnings.append(warning)
    return ContentTypeMap(entries), warnings


def _list_id_map_from_pairs(resolved: Sequence[tuple[SPList, SPList]]) -> dict[str, str]:
    """Normalized source->target list ids for the lists resolved for one web."""
    result: dict[str, str] = {}
    for source_list, target_list in resolved:
        source_id = normalize_guid(source_list.id)
        target_id = normalize_guid(target_list.id)
        if source_id and target_id:
            result[source_id] = target_id
    return result


def _list_id_map(source_web: Web, target_web: Web) -> dict[str, str]:
    """Match lists across two webs by title, keyed by normalized source list id.

    Used by the single-list resolver, which only ever provisions one list and so
    cannot build the map from the resolved pairs. A lookup referencing a list that
    exists on both sides is repointed; one referencing a list absent from the
    target is left unresolved (and skipped with a warning).
    """
    targets_by_title = _target_list_ids_by_title(target_web)
    result: dict[str, str] = {}
    for source_list in source_web.lists.get().execute_query():
        source_id = normalize_guid(source_list.id)
        title = source_list.title
        target_id = targets_by_title.get(title) if title else None
        if source_id and target_id:
            result[source_id] = target_id
    return result


def _target_list_ids_by_title(target_web: Web) -> dict[str, str]:
    """Normalized target list ids keyed by list title for one target web."""
    result: dict[str, str] = {}
    for target_list in target_web.lists.get().execute_query():
        title = target_list.title
        target_id = normalize_guid(target_list.id)
        if title and target_id:
            result[title] = target_id
    return result


def _attach_warnings(target: Target, warnings: list[str]) -> None:
    """Record structure-provisioning warnings on the target adapter for the session."""
    target.warnings.extend(warnings)


def _list_adapters(
    source_list: SPList, target_list: SPList, *, content_type_map: ContentTypeMap | None = None
) -> tuple[Source, Target]:
    """Build the source/target adapter pair for one resolved list/library."""
    if is_document_library(source_list):
        source = SharePointLibrarySource(source_list.root_folder, sp_list=source_list)
        folder = target_list.root_folder.get().execute_query()
        target = SharePointLibraryTarget(folder, sp_list=target_list, content_type_map=content_type_map)
    else:
        source = SharePointListSource(source_list)
        target = SharePointListTarget(target_list, content_type_map=content_type_map)
    return source, target


def _ensure_target_list(context: ClientContext, source_list: SPList) -> SPList:
    """The target list matching ``source_list``'s title, created (type only) if absent."""
    title = source_list.title
    if not title:
        raise ValueError("cannot resolve a target list for a source list without a title")
    target = context.web.lists.ensure_list(title, template_type=_template_type(source_list))
    target.execute_query()
    return target


def _ensure_target_web(parent_context: ClientContext, source_web: Web) -> tuple[Web, ClientContext]:
    """The target subsite mirroring ``source_web`` (created if absent), plus its context.

    Returns a ``(target_web, target_context)`` pair; ``target_context`` is rooted at
    the target subsite so its lists resolve there (a subweb's sub-collections resolve
    against the context root otherwise).
    """
    leaf, title, template = _web_identity(source_web)
    for existing in parent_context.web.webs.get().execute_query():
        if _web_leaf(existing) == leaf.casefold():
            return existing, _context_for(parent_context, _web_url(existing))
    created = parent_context.web.webs.add(WebCreationInformation(Title=title, Url=leaf, WebTemplate=template))
    created.execute_query()
    created_url = _web_url(created) or f"{parent_context.base_url.rstrip('/')}/{leaf.strip('/')}"
    return created, _context_for(parent_context, created_url)


def _web_identity(web: Web) -> tuple[str, str, str]:
    """A web's URL leaf, display title and template (REST-creation inputs)."""
    raw = _web_url(web)
    leaf = raw.rstrip("/").rsplit("/", 1)[-1]
    title = web.title or leaf
    template = web.web_template or "STS#3"
    return leaf, title, template


def _web_url(web: Web) -> str:
    """A web's absolute URL, or its server-relative URL when only that is loaded."""
    for name in ("Url", "ServerRelativeUrl"):
        value = web.get_property(name)
        if value:
            return str(value)
    return web.server_relative_url or web.url or ""


def _web_leaf(web: Web) -> str:
    """A web's URL leaf, case-folded, for identity matching across tenants."""
    return _web_identity(web)[0].casefold()


def _template_type(source_list: SPList) -> ListTemplateType:
    value = source_list.base_template
    if value is not None:
        try:
            return ListTemplateType(value)
        except ValueError:
            pass
    return ListTemplateType.DocumentLibrary if is_document_library(source_list) else ListTemplateType.GenericList


def _file_share(
    task: MigrationTask, context: ClientContext, settings: "MigrationSettings | None"
) -> tuple[Source, Target]:
    if not task.file_share_source:
        raise ValueError("a file-share task requires file_share_source")
    source = FileSystemSource(task.file_share_source)
    target_context = _context_for(context, task.target_site_url)
    target_list, folder = _target_folder(target_context, task)
    return source, _build_target(task, target_context, settings, target_list, folder)


def _sharepoint(
    task: MigrationTask,
    context: ClientContext,
    settings: "MigrationSettings | None",
    *,
    provision_structure: bool = True,
) -> tuple[Source, Target]:
    source_context = _context_for(context, task.sharepoint_source_site_url)
    target_context = _context_for(context, task.target_site_url)
    source_list = source_context.web.get_list_by_title(task.source_list).get().execute_query()
    source = _list_source(source_list)
    target_list, folder = _target_folder(target_context, task)
    # Always replay structure over REST. The server-side package path does not
    # emit columns/content types/views yet, so skipping this would silently drop
    # them from the target (the package builder only carries the library, folders,
    # files, and file versions).
    if provision_structure:
        list_id_map = _list_id_map(source_context.web, target_context.web)
        content_type_map, structure_warnings = _provision_structure(source_list, target_list, list_id_map)
    else:
        content_type_map, structure_warnings = None, []
    target = _build_target(task, target_context, settings, target_list, folder, content_type_map=content_type_map)
    _attach_warnings(target, structure_warnings)
    return source, target


def _list_source(source_list: SPList) -> Source:
    if is_document_library(source_list):
        return SharePointLibrarySource(source_list.root_folder, sp_list=source_list)
    return SharePointListSource(source_list)


def _context_for(context: ClientContext, url: str | None) -> ClientContext:
    """The registered context, or an authenticated clone for another site URL.

    Source and target may live in different site collections of the same tenant;
    the clone reuses the registered context's authentication and transport.
    """
    if not url or _same_site(context.base_url, url):
        return context
    return context.clone(url)


def _same_site(a: str | None, b: str | None) -> bool:
    return (a or "").rstrip("/").casefold() == (b or "").rstrip("/").casefold()


def _target_folder(context: ClientContext, task: MigrationTask) -> tuple[SPList, Folder]:
    """The target list and (when set) the relative target subfolder."""
    target_list = context.web.get_list_by_title(task.target_list).get().execute_query()
    folder = target_list.root_folder.get().execute_query()
    if task.target_list_relative_path:
        url = f"{(folder.server_relative_url or '').rstrip('/')}/{task.target_list_relative_path.strip('/')}"
        folder = context.web.get_folder_by_server_relative_url(url)
    return target_list, folder


def _build_target(
    task: MigrationTask,
    context: ClientContext,
    settings,
    target_list: SPList,
    folder: Folder,
    *,
    content_type_map: ContentTypeMap | None = None,
) -> Target:
    if settings is not None and settings.use_migration_api:
        return _package_target(task, context, target_list)
    if is_document_library(target_list):
        return SharePointLibraryTarget(folder, sp_list=target_list, content_type_map=content_type_map)
    return SharePointListTarget(target_list, content_type_map=content_type_map)


def _package_target(task: MigrationTask, context: ClientContext, library: SPList) -> SharePointPackageTarget:
    """The server-side Migration API target (provisions containers)."""
    from urllib.parse import urlparse

    from office365.migration.sharepoint.package_target import SharePointPackageTarget

    web = context.web.get().execute_query()
    root = library.root_folder
    root.ensure_properties(["UniqueId", "ServerRelativeUrl"]).execute_query()
    parent = root.parent_folder.ensure_property("UniqueId")
    parent.execute_query()
    containers = context.site.provision_migration_containers().execute_query().value
    return SharePointPackageTarget(
        context.site,
        web.id,
        content_uri=containers.DataContainerUri,
        manifest_uri=containers.MetadataContainerUri,
        encryption_key=containers.EncryptionKey,
        site_url=context.base_url,
        list_title=library.title or "",
        list_url=root.server_relative_url,
        web_url=urlparse(context.base_url).path or "/",
        root_folder_id=root.unique_id,
        root_folder_parent_id=parent.unique_id,
        source_type="FileShare" if task.kind == FILE_SHARE else "SharePointOnline",
    )
