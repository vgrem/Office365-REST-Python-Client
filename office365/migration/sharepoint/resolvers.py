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
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any, Iterable, Sequence

from office365.migration.adapters.filesystem import FileSystemSource
from office365.migration.map import ContentTypeMap
from office365.migration.sharepoint.adapters import (
    SharePointLibrarySource,
    SharePointLibraryTarget,
    SharePointListSource,
    SharePointListTarget,
)
from office365.migration.sharepoint.structure import capture_list_structure, provision_list_structure
from office365.migration.tasks import FILE_SHARE, SHAREPOINT, MigrationTask
from office365.sharepoint.webs.creation_information import WebCreationInformation

if TYPE_CHECKING:
    from office365.migration.settings import MigrationSettings

logger = logging.getLogger(__name__)

__all__ = ["is_document_library", "is_migratable_list", "resolve_site_task", "resolve_task"]

#: SharePoint's own infrastructure templates (user information, catalogs,
#: workflow/translation plumbing) plus the Site Pages library, which needs
#: page-aware handling the generic adapters do not provide yet.
_SYSTEM_BASE_TEMPLATES = frozenset({112, 113, 114, 115, 116, 117, 118, 119, 121, 122, 123, 124, 125, 126, 127, 130})

#: ``SPBaseType.DocumentLibrary`` — libraries hold files; everything else is a
#: record list.
_DOCUMENT_LIBRARY = 1


def is_document_library(sp_list: Any) -> bool:
    """Whether a SharePoint list is a document library (holds files, not records)."""
    return sp_list.base_type == _DOCUMENT_LIBRARY


def is_migratable_list(sp_list: Any) -> bool:
    """Whether a list/library takes part in a whole-site migration.

    Skips hidden lists, SharePoint infrastructure templates, and system lists
    that cannot be deleted (e.g. ``User Information``).
    """
    if getattr(sp_list, "hidden", False):
        return False
    if getattr(sp_list, "allow_deletion", None) is False:
        return False
    return getattr(sp_list, "base_template", None) not in _SYSTEM_BASE_TEMPLATES


def resolve_task(
    task: MigrationTask,
    context: Any,
    settings: "MigrationSettings | None" = None,
    *,
    provision_structure: bool = True,
) -> tuple[Any, Any]:
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


def resolve_site_task(
    task: MigrationTask,
    context: Any,
    settings: "MigrationSettings | None" = None,
    *,
    include: Sequence[str] | None = None,
    exclude: Sequence[str] | None = None,
    provision_structure: bool = True,
    include_subwebs: bool = False,
    warnings: list[str] | None = None,
) -> list[tuple[Any, Any]]:
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
        warnings: Optional sink for resolution-level notes (subsites skipped).
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

    pairs: list[tuple[Any, Any]] = []
    _resolve_web(
        source_context,
        target_context,
        include_titles,
        exclude_titles,
        provision_structure,
        include_subwebs,
        warnings if warnings is not None else [],
        pairs,
    )
    return pairs


def _resolve_web(
    source_context: Any,
    target_context: Any,
    include_titles: set[str] | None,
    exclude_titles: set[str],
    provision_structure: bool,
    include_subwebs: bool,
    warnings: list[str],
    pairs: list[tuple[Any, Any]],
) -> None:
    """Resolve one web's lists, then recurse into its subsites when requested."""
    source_lists: Iterable[Any] = source_context.web.lists.get().execute_query()
    for source_list in source_lists:
        title = getattr(source_list, "title", None)
        if not title or title in exclude_titles:
            continue
        if include_titles is not None and title not in include_titles:
            continue
        if not is_migratable_list(source_list):
            continue
        target_list = _ensure_target_list(target_context, source_list)
        if provision_structure:
            content_type_map, structure_warnings = _provision_structure(source_list, target_list)
        else:
            content_type_map, structure_warnings = None, []
        source, target = _list_adapters(source_list, target_list, content_type_map=content_type_map)
        _attach_warnings(target, structure_warnings)
        pairs.append((source, target))

    child_webs = list(source_context.web.webs.get().execute_query())
    if not child_webs:
        return
    if not include_subwebs:
        names = [getattr(web, "title", None) or _web_identity(web)[0] for web in child_webs]
        note = (
            f"{len(child_webs)} subsite(s) were not migrated (pass include_subwebs=True to "
            f"include them): {', '.join(names)}"
        )
        logger.warning(note)
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
            warnings,
            pairs,
        )


def _provision_structure(source_list: Any, target_list: Any) -> tuple[ContentTypeMap, list[str]]:
    """Capture the source list structure and replay it onto the target list.

    Structure provisioning is best-effort where SharePoint Online constrains it
    (a fresh column cannot be attached to a custom content type over REST); those
    columns are reported as warnings rather than aborting the resolution.

    Returns:
        The content-type identity map built while provisioning (SharePoint
        assigns recreated list content types a fresh ``StringId``, so items
        carrying the source ``ContentTypeId`` must be rewritten to the target
        one) and the human-readable warnings the target did not apply.
    """
    structure = capture_list_structure(source_list)
    entries: dict[str, str] = {}
    warnings: list[str] = []
    for warning in provision_list_structure(target_list, structure, content_type_map=entries):
        logger.warning("list %r: %s", getattr(source_list, "title", None), warning)
        warnings.append(warning)
    return ContentTypeMap(entries), warnings


def _attach_warnings(target: Any, warnings: list[str]) -> None:
    """Record structure-provisioning warnings on the target adapter for the session."""
    if not warnings:
        return
    bucket = getattr(target, "warnings", None)
    if bucket is None:
        target.warnings = list(warnings)
    else:
        bucket.extend(warnings)


def _list_adapters(
    source_list: Any, target_list: Any, *, content_type_map: ContentTypeMap | None = None
) -> tuple[Any, Any]:
    """Build the source/target adapter pair for one resolved list/library."""
    if is_document_library(source_list):
        source = SharePointLibrarySource(source_list.root_folder, sp_list=source_list)
        folder = target_list.root_folder.get().execute_query()
        target = SharePointLibraryTarget(folder)
    else:
        source = SharePointListSource(source_list)
        target = SharePointListTarget(target_list, content_type_map=content_type_map)
    return source, target


def _ensure_target_list(context: Any, source_list: Any) -> Any:
    """The target list matching ``source_list``'s title, created (type only) if absent."""
    target = context.web.lists.ensure_list(source_list.title, template_type=_template_type(source_list))
    target.execute_query()
    return target


def _ensure_target_web(parent_context: Any, source_web: Any) -> tuple[Any, Any]:
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


def _web_identity(web: Any) -> tuple[str, str, str]:
    """A web's URL leaf, display title and template (REST-creation inputs)."""
    raw = _web_url(web)
    leaf = raw.rstrip("/").rsplit("/", 1)[-1]
    title = getattr(web, "title", None) or leaf
    template = getattr(web, "web_template", None) or "STS#3"
    return leaf, title, template


def _web_url(web: Any) -> str:
    """A web's absolute URL, or its server-relative URL when only that is loaded."""
    for name in ("Url", "ServerRelativeUrl"):
        value = web.get_property(name) if hasattr(web, "get_property") else None
        if value:
            return value
    value = getattr(web, "server_relative_url", None) or getattr(web, "url", None)
    return value or ""


def _web_leaf(web: Any) -> str:
    """A web's URL leaf, case-folded, for identity matching across tenants."""
    return _web_identity(web)[0].casefold()


def _template_type(source_list: Any) -> Any:
    from office365.sharepoint.lists.templates.type import ListTemplateType

    value = getattr(source_list, "base_template", None)
    if value is not None:
        try:
            return ListTemplateType(value)
        except ValueError:
            pass
    return ListTemplateType.DocumentLibrary if is_document_library(source_list) else ListTemplateType.GenericList


def _file_share(task: MigrationTask, context: Any, settings: "MigrationSettings | None") -> tuple[Any, Any]:
    if not task.file_share_source:
        raise ValueError("a file-share task requires file_share_source")
    source = FileSystemSource(task.file_share_source)
    target_context = _context_for(context, task.target_site_url)
    target_list, folder = _target_folder(target_context, task)
    return source, _build_target(task, target_context, settings, target_list, folder)


def _sharepoint(
    task: MigrationTask,
    context: Any,
    settings: "MigrationSettings | None",
    *,
    provision_structure: bool = True,
) -> tuple[Any, Any]:
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
        content_type_map, structure_warnings = _provision_structure(source_list, target_list)
    else:
        content_type_map, structure_warnings = None, []
    target = _build_target(task, target_context, settings, target_list, folder, content_type_map=content_type_map)
    _attach_warnings(target, structure_warnings)
    return source, target


def _list_source(source_list: Any) -> Any:
    if is_document_library(source_list):
        return SharePointLibrarySource(source_list.root_folder, sp_list=source_list)
    return SharePointListSource(source_list)


def _context_for(context: Any, url: str | None) -> Any:
    """The registered context, or an authenticated clone for another site URL.

    Source and target may live in different site collections of the same tenant;
    the clone reuses the registered context's authentication and transport.
    """
    if not url or _same_site(context.base_url, url):
        return context
    return context.clone(url)


def _same_site(a: str | None, b: str | None) -> bool:
    return (a or "").rstrip("/").casefold() == (b or "").rstrip("/").casefold()


def _target_folder(context: Any, task: MigrationTask) -> tuple[Any, Any]:
    """The target list and (when set) the relative target subfolder."""
    target_list = context.web.get_list_by_title(task.target_list).get().execute_query()
    folder = target_list.root_folder.get().execute_query()
    if task.target_list_relative_path:
        url = f"{(folder.server_relative_url or '').rstrip('/')}/{task.target_list_relative_path.strip('/')}"
        folder = context.web.get_folder_by_server_relative_url(url)
    return target_list, folder


def _build_target(
    task: MigrationTask,
    context: Any,
    settings,
    target_list: Any,
    folder: Any,
    *,
    content_type_map: ContentTypeMap | None = None,
) -> Any:
    if settings is not None and settings.use_migration_api:
        return _package_target(task, context, target_list)
    if is_document_library(target_list):
        return SharePointLibraryTarget(folder)
    return SharePointListTarget(target_list, content_type_map=content_type_map)


def _package_target(task: MigrationTask, context: Any, library: Any) -> Any:
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
        list_title=library.title,
        list_url=root.server_relative_url,
        web_url=urlparse(context.base_url).path or "/",
        root_folder_id=root.unique_id,
        root_folder_parent_id=parent.unique_id,
        source_type="FileShare" if task.kind == FILE_SHARE else "SharePointOnline",
    )
