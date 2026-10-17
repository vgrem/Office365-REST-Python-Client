"""Package builder — assemble a SharePoint Migration API package.

Walks a document library's files and folders into the manifest XML documents
(``Manifest.xml`` / ``ExportSettings.xml`` / ``SystemData.xml`` / ``UserGroup.xml``)
plus the content blobs, ready to stage in Azure Storage and submit via
``Site.create_migration_job`` / ``create_migration_job_encrypted``.

The ``Manifest.xml`` shape follows the working ``MigrationApiDemo`` sample: a
library root ``SPFolder``, the ``SPDocumentLibrary``, then an ``SPFolder`` per
subfolder and an ``SPFile`` per file (no ``SPWeb``/``SPList`` objects — those are
the target system objects). Content blobs are named after the file's GUID and
referenced from ``<File FileValue="…">``; older versions get a ``<guid>.<version>``
blob. IDs are **deterministic** (``uuid5`` of the item path), so rebuilding the
same content yields the same package.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path, PurePosixPath

from office365.migration.base import normalize_puid
from office365.migration.package.manifest_xml import (
    LOOKUP_LIST_MAP_NS,
    REQUIREMENTS_NS,
    VIEW_FORMS_LIST_NS,
    Assignment,
    DeploymentObject,
    ExportSettings,
    Group,
    Manifest,
    ManifestElement,
    ManifestObject,
    Role,
    RoleAssignment,
    RootObject,
    RootObjectMap,
    SharedWithEvent,
    SystemData,
    SystemObject,
    User,
    UserGroupMap,
    empty_document,
)

# Stable namespace so item GUIDs are reproducible across runs.
DEFAULT_NAMESPACE = uuid.uuid5(uuid.NAMESPACE_URL, "office365-rest-python-client/migration")

# ``SPListTemplateType`` for a document library (a free string in the schema).
_DOCUMENT_LIBRARY_TEMPLATE = "DocumentLibrary"

__all__ = ["DEFAULT_NAMESPACE", "Package", "PackageBuilder"]


def _normalize(path: str) -> str:
    """Normalize a library-relative path (no leading/trailing slash, ``/`` separators)."""
    return path.replace("\\", "/").strip("/")


def _is_decimal(value: str) -> bool:
    """Whether ``value`` is a base-10 integer string (the API's ``PermMask`` format)."""
    try:
        int(value, 10)
    except (TypeError, ValueError):
        return False
    return True


def _append_shared_with(item: ManifestObject, events: list[SharedWithEvent]) -> None:
    """Append "Shared with Me" events to a list item (reusing its existing block)."""
    for child in item.children:
        if child.name == "SharedWithEvents":
            child.children.extend(event.to_element() for event in events)
            return
    item.children.append(ManifestElement("SharedWithEvents", children=[event.to_element() for event in events]))


@dataclass
class Package:
    """An assembled migration package: manifest documents + content blobs.

    ``Requirements.xml`` / ``RootObjectMap.xml`` / ``LookupListMap.xml`` /
    ``ViewFormsList.xml`` are documented as optional, but the ingestion service
    fetches them by name — a missing one fails the job with a 404.
    """

    manifest: bytes
    export_settings: bytes
    system_data: bytes
    user_group_map: bytes
    requirements: bytes = b""
    root_object_map: bytes = b""
    lookup_list_map: bytes = b""
    view_forms_list: bytes = b""
    content: dict[str, bytes] = field(default_factory=dict)

    def blobs(self) -> dict[str, bytes]:
        """The manifest-package blobs by file name (go to the manifest container)."""
        return {
            "Manifest.xml": self.manifest,
            "ExportSettings.xml": self.export_settings,
            "SystemData.xml": self.system_data,
            "UserGroup.xml": self.user_group_map,
            "Requirements.xml": self.requirements,
            "RootObjectMap.xml": self.root_object_map,
            "LookupListMap.xml": self.lookup_list_map,
            "ViewFormsList.xml": self.view_forms_list,
        }

    def save(self, directory: str | Path) -> list[Path]:
        """Write the manifest files and content blobs under ``directory``.

        Layout: ``<directory>/manifest/<Name>.xml`` and
        ``<directory>/content/<blob>`` — matching the two Azure containers.
        """
        root = Path(directory)
        (root / "manifest").mkdir(parents=True, exist_ok=True)
        (root / "content").mkdir(parents=True, exist_ok=True)
        written: list[Path] = []
        for name, data in self.blobs().items():
            path = root / "manifest" / name
            path.write_bytes(data)
            written.append(path)
        for name, data in self.content.items():
            path = root / "content" / name
            path.write_bytes(data)
            written.append(path)
        return written


class PackageBuilder:
    """Assembles a document-library migration package."""

    def __init__(
        self,
        site_url: str,
        *,
        web_id: str | None = None,
        web_url: str = "/",
        list_id: str | None = None,
        list_title: str = "Documents",
        list_url: str | None = None,
        root_folder_id: str | None = None,
        root_folder_parent_id: str | None = None,
        source_type: str = "SharePointOnline",
        include_security: str = "None",
        namespace: uuid.UUID | None = None,
    ) -> None:
        self._namespace = namespace or DEFAULT_NAMESPACE
        self._web_id = web_id or str(self._guid("web"))
        self._web_url = web_url
        self._list_id = list_id or str(self._guid("list"))
        self._list_title = list_title
        self._list_url = list_url or f"{web_url.rstrip('/')}/{list_title}"
        self._root_folder_id = root_folder_id or self._list_id
        self._root_folder_parent_id = root_folder_parent_id or self._web_id
        self._export = ExportSettings(
            site_url=site_url,
            source_type=source_type,
            include_security=include_security,
            export_objects=[DeploymentObject(id=self._list_id, type="List", parent_id=self._web_id)],
        )
        self._manifest = Manifest()
        self._user_group_map = UserGroupMap()
        self._content: dict[str, bytes] = {}
        self._folders: dict[str, str] = {}
        self._files: dict[str, str] = {}
        self._list_item_int_id = 0
        self._roles: list[Role] = []
        self._role_assignments: list[RoleAssignment] = []
        self._roles_id = str(self._guid("roles"))
        self._role_assignments_id = str(self._guid("roleassignments"))
        self._principal_seq = 0
        self._security_added = False
        self._list_items: dict[str, ManifestObject] = {}
        self._add_root()
        self._add_document_library()

    # ── Content ──────────────────────────────────────────────────

    def add_folder(
        self,
        path: str,
        *,
        time_created: datetime | str | None = None,
        time_last_modified: datetime | str | None = None,
        author: str | None = None,
        editor: str | None = None,
    ) -> str:
        """Add a folder (and any missing parents); returns its GUID.

        ``author``/``editor`` are ``UserGroup.xml`` integer ids (from
        :meth:`add_user`), not login names.
        """
        path = _normalize(path)
        if path in self._folders:
            return self._folders[path]
        parent_id = self._parent_id(path)
        folder_id = str(self._guid(f"folder:{path}"))
        self._manifest.add(
            ManifestObject(
                id=folder_id,
                object_type="SPFolder",
                element="Folder",
                attributes={
                    "Id": folder_id,
                    "Name": path,
                    "Url": self._url(path),
                    "ParentFolderId": parent_id,
                    "ParentWebId": self._web_id,
                    "ParentWebUrl": self._web_url,
                    "ContainingDocumentLibrary": self._list_id,
                    "TimeCreated": time_created,
                    "TimeLastModified": time_last_modified,
                    "Author": author,
                    "ModifiedBy": editor,
                },
                parent_id=parent_id,
                parent_web_id=self._web_id,
                parent_web_url=self._web_url,
                url=self._url(path),
            )
        )
        self._folders[path] = folder_id
        return folder_id

    def add_file(
        self,
        path: str,
        content: bytes,
        *,
        time_created: datetime | str | None = None,
        time_last_modified: datetime | str | None = None,
        version: str = "1.0",
        versions: list[tuple[str, bytes]] | None = None,
        list_item_int_id: int | None = None,
        author: str | None = None,
        editor: str | None = None,
        with_list_item: bool = True,
        fields: dict[str, str] | None = None,
        shared_with: list[SharedWithEvent] | None = None,
    ) -> str:
        """Add a file (and any missing parent folders); returns its GUID.

        Args:
            path: Library-relative path.
            content: The current version's bytes.
            version: The current version label (e.g. ``"1.0"``).
            versions: Older versions as ``(version, content)`` pairs, **oldest
                first**. The current version (``content``/``version``) is appended
                automatically: the Migration API builds history from ``<Versions>``
                and promotes its last entry to the current version (the outer
                ``File`` blob is ignored once ``<Versions>`` is present).
            list_item_int_id: Optional list-item integer id to preserve.
            author: Original author — the ``UserGroup.xml`` **integer id** (from
                :meth:`add_user`), not a login name.
            editor: Last modified by — likewise a ``UserGroup.xml`` integer id.
        """
        path = _normalize(path)
        parent_id = self._parent_id(path)
        file_id = str(self._guid(f"file:{path}"))
        url = self._url(path)
        self._content[file_id] = content
        self._list_item_int_id += 1
        version_rows: list[ManifestElement] = []
        older_versions = list(versions or [])
        if older_versions:
            # The API promotes the LAST <Versions> entry to current and ignores the
            # outer File blob, so the current version must be listed last.
            older_versions.append((version, content))
        for older_version, older_content in older_versions:
            blob = f"{file_id}.{older_version}"
            self._content[blob] = older_content
            version_rows.append(
                ManifestElement(
                    "File",
                    {
                        "Id": file_id,
                        "Name": path,
                        "Url": url,
                        "ParentWebId": self._web_id,
                        "ParentWebUrl": self._web_url,
                        "ParentId": parent_id,
                        "ListId": self._list_id,
                        "FileValue": blob,
                        "Version": older_version,
                    },
                )
            )
        children = [ManifestElement("Versions", children=version_rows)] if version_rows else []
        self._manifest.add(
            ManifestObject(
                id=file_id,
                object_type="SPFile",
                element="File",
                attributes={
                    "Id": file_id,
                    "Name": path,
                    "Url": url,
                    "ParentId": parent_id,
                    "ParentWebId": self._web_id,
                    "ParentWebUrl": self._web_url,
                    "ListId": self._list_id,
                    "FileValue": file_id,
                    "ListItemIntId": list_item_int_id or self._list_item_int_id,
                    "Version": version,
                    "TimeCreated": time_created,
                    "TimeLastModified": time_last_modified,
                    "Author": author,
                    "ModifiedBy": editor,
                },
                children=children,
                parent_id=parent_id,
                parent_web_id=self._web_id,
                parent_web_url=self._web_url,
                url=url,
            )
        )
        self._files[path] = file_id
        if with_list_item:
            # the service silently skips an SPFile that has no matching SPListItem
            self.add_list_item(
                url,
                doc_id=file_id,
                parent_folder_id=parent_id,
                name=path,
                int_id=list_item_int_id or self._list_item_int_id,
                version=version,
                time_created=time_created,
                time_last_modified=time_last_modified,
                author=author,
                editor=editor,
                fields=fields if fields is not None else {"Title": PurePosixPath(path).name},
                shared_with=shared_with,
            )
        return file_id

    def add_user(
        self,
        login: str,
        *,
        name: str | None = None,
        email: str | None = None,
        system_id: str | None = None,
        is_site_admin: bool = False,
    ) -> int:
        """Register a user in ``UserGroup.xml``; returns its integer id.

        ``system_id`` (when given) must be the user's PUID
        (``UserInfo.UserId.NameId``, a 16-character hex string); the service
        rejects a GUID, a claims login, or the app principal with a
        ``System.FormatException`` that fails the job. A ``0x`` prefix or stray
        whitespace is stripped, so only the digits reach ``SystemId``.
        """
        puid = normalize_puid(system_id)
        if system_id is not None and puid is None:
            raise ValueError(f"system_id must be a PUID (16-char hex), got {system_id!r}")
        user_id = self._next_principal_id()
        self._user_group_map.add_user(
            User(
                id=user_id,
                name=name or login,
                login=login,
                email=email,
                system_id=puid,
                is_site_admin=is_site_admin,
            )
        )
        return user_id

    def add_group(
        self,
        name: str,
        *,
        description: str | None = None,
        owner: int | None = None,
        members: list[int] | None = None,
    ) -> int:
        """Register a SharePoint group in ``UserGroup.xml``; returns its integer id."""
        group_id = self._next_principal_id()
        self._user_group_map.groups.append(
            Group(id=group_id, name=name, description=description, owner=owner, members=list(members or []))
        )
        return group_id

    def add_role(
        self,
        role_id: str,
        title: str,
        perm_mask: str,
        *,
        hidden: bool = False,
        description: str | None = None,
        role_order: str | None = None,
        role_type: str | None = None,
    ) -> None:
        """Register a permission level (a ``DeploymentRoles`` ``<Role>``).

        ``perm_mask`` must be a **decimal** integer string (e.g. ``"756052856929"``):
        the service parses ``PermMask`` as a decimal, and a hex ``"0x..."`` mask
        fails the ingestion job with a ``FormatException``. Use a non-system
        ``role_id`` (below ``1073741824``); a system id is rejected by the service
        with "Updates to system roles is not allowed". The service matches a role
        by ``title`` against the target's existing permission levels, so reusing an
        existing title updates that level rather than creating a duplicate.
        """
        if not _is_decimal(perm_mask):
            raise ValueError(f"perm_mask must be a decimal integer string, got {perm_mask!r}")
        if any(role.id == role_id for role in self._roles):
            return
        self._roles.append(Role(role_id, title, perm_mask, hidden, description, role_order, role_type))

    def add_role_assignment(
        self,
        *,
        object_id: str,
        object_url: str,
        object_type: str = "2",
        role_def_web_id: str,
        role_def_web_url: str,
        assignments: list[tuple[str, int]],
        scope_id: str | None = None,
        anonymous_perm_mask: str = "0",
    ) -> None:
        """Register an ACL scope — ``(role_id, principal_id)`` grants on an object.

        Args:
            object_id/object_url: the secured object (a file/folder GUID + URL).
            object_type: the secured-object kind — a numeric enum the service parses
              (``0`` web, ``1`` list, ``2`` item/file; live-validated: ``2`` breaks
              inheritance for a file).
            role_def_web_id/role_def_web_url: the web whose role definitions apply.
            assignments: ``(RoleId, PrincipalId)`` pairs (principal ids from ``UserGroup.xml``).
            scope_id: the scope the assignment applies to (defaults to ``object_id``).
        """
        self._role_assignments.append(
            RoleAssignment(
                object_id=object_id,
                object_url=object_url,
                object_type=object_type,
                role_def_web_id=role_def_web_id,
                role_def_web_url=role_def_web_url,
                scope_id=scope_id or object_id,
                assignments=[Assignment(role_id=role, principal_id=principal) for role, principal in assignments],
                anonymous_perm_mask=anonymous_perm_mask,
            )
        )

    def add_list_item(
        self,
        file_url: str,
        *,
        item_id: str | None = None,
        doc_id: str | None = None,
        parent_folder_id: str | None = None,
        name: str | None = None,
        int_id: int | None = None,
        version: str = "1.0",
        time_created: datetime | str | None = None,
        time_last_modified: datetime | str | None = None,
        author: str | None = None,
        editor: str | None = None,
        fields: dict[str, str] | None = None,
        shared_with: list[SharedWithEvent] | None = None,
    ) -> str:
        """Add an ``SPListItem`` for a file (metadata + "Shared with Me" events); returns its GUID.

        ``doc_id`` links the item to its ``SPFile`` (``DocType=File``); ``fields``
        are the item's field values (the serializer requires a ``<Fields>`` member).
        ``author``/``editor`` are ``UserGroup.xml`` integer ids, not login names.
        """
        existing = self._list_items.get(file_url)
        if existing is not None:
            if shared_with:
                _append_shared_with(existing, shared_with)
            return existing.id
        item_id = item_id or str(self._guid(f"listitem:{file_url}"))
        children = [
            ManifestElement(
                "Fields",
                children=[
                    ManifestElement("Field", {"Name": field, "Value": value, "Type": "Text"})
                    for field, value in (fields or {}).items()
                ],
            )
        ]
        if shared_with:
            children.append(ManifestElement("SharedWithEvents", children=[event.to_element() for event in shared_with]))
        item = ManifestObject(
            id=item_id,
            object_type="SPListItem",
            element="ListItem",
            attributes={
                "Id": item_id,
                "ParentWebId": self._web_id,
                "ParentWebUrl": self._web_url,
                "TimeCreated": time_created,
                "TimeLastModified": time_last_modified,
                "Author": author,
                "ModifiedBy": editor,
                "FileUrl": file_url,
                "DocType": "File",
                "ParentFolderId": parent_folder_id or self._root_folder_id,
                "ParentListId": self._list_id,
                "Name": name or file_url.rsplit("/", 1)[-1],
                "DirName": self._list_url,
                "IntId": int_id,
                "DocId": doc_id,
                "Version": version,
                "ModerationStatus": "Approved",
            },
            children=children,
            parent_id=self._list_id,
            parent_web_id=self._web_id,
            parent_web_url=self._web_url,
            url=file_url,
        )
        self._manifest.add(item)
        self._list_items[file_url] = item
        return item_id

    def object_id(self, path: str) -> str | None:
        """The manifest GUID of a file/folder already added (``None`` if absent)."""
        key = _normalize(path)
        return self._files.get(key) or self._folders.get(key)

    def item_url(self, path: str) -> str:
        """The website-relative URL of an item path (mirrors the manifest's ``Url``)."""
        return self._url(_normalize(path))

    def set_include_security(self, value: str) -> None:
        """Set ``ExportSettings/@IncludeSecurity`` (e.g. ``"All"`` to carry ACLs)."""
        self._export.include_security = value

    def build(self) -> Package:
        """Render the manifest documents and freeze the content blobs."""
        self._add_security_objects()
        system_data = SystemData(
            system_objects=[
                SystemObject(id=self._web_id, type="Web", url=self._web_url),
                SystemObject(id=self._list_id, type="List", url=self._list_url),
            ]
        )
        root_object_map = RootObjectMap(
            objects=[
                RootObject(
                    id=self._list_id,
                    type="List",
                    parent_id=self._web_id,
                    web_url=self._web_url,
                    url=self._list_url,
                )
            ]
        )
        return Package(
            manifest=self._manifest.to_xml(),
            export_settings=self._export.to_xml(),
            system_data=system_data.to_xml(),
            user_group_map=self._user_group_map.to_xml(),
            requirements=empty_document(REQUIREMENTS_NS, "Requirements"),
            root_object_map=root_object_map.to_xml(),
            lookup_list_map=empty_document(LOOKUP_LIST_MAP_NS, "LookupLists"),
            view_forms_list=empty_document(VIEW_FORMS_LIST_NS, "ViewFormsList"),
            content=dict(self._content),
        )

    # ── Manifest objects ─────────────────────────────────────────

    def _add_root(self) -> None:
        """The library root folder (``SPFolder``) — the package's entry point."""
        self._manifest.add(
            ManifestObject(
                id=self._root_folder_id,
                object_type="SPFolder",
                element="Folder",
                attributes={
                    "Id": self._root_folder_id,
                    "Name": self._list_name,
                    "Url": self._list_name,
                    "ParentFolderId": self._root_folder_parent_id,
                    "ParentWebId": self._web_id,
                    "ParentWebUrl": self._web_url,
                    "ContainingDocumentLibrary": self._list_id,
                },
                parent_id=self._root_folder_parent_id,
                parent_web_id=self._web_id,
                parent_web_url=self._web_url,
                url=self._list_url,
            )
        )

    def _add_document_library(self) -> None:
        """The target document library (``SPDocumentLibrary``)."""
        self._manifest.add(
            ManifestObject(
                id=self._list_id,
                object_type="SPDocumentLibrary",
                element="DocumentLibrary",
                attributes={
                    "Id": self._list_id,
                    "BaseTemplate": _DOCUMENT_LIBRARY_TEMPLATE,
                    "ParentWebId": self._web_id,
                    "ParentWebUrl": self._web_url,
                    "RootFolderId": self._root_folder_id,
                    "RootFolderUrl": self._list_url,
                    "Title": self._list_title,
                },
                parent_id=self._web_id,
                parent_web_id=self._web_id,
                parent_web_url=self._web_url,
                url=self._list_url,
            )
        )

    # ── Helpers ──────────────────────────────────────────────────

    @property
    def _list_name(self) -> str:
        return self._list_url.rstrip("/").rsplit("/", 1)[-1]

    def _add_security_objects(self) -> None:
        """Emit the ``DeploymentRoles`` / ``DeploymentRoleAssignments`` objects (once)."""
        if self._security_added:
            return
        self._security_added = True
        if self._roles:
            self._manifest.add(
                ManifestObject(
                    id=self._roles_id,
                    object_type="DeploymentRoles",
                    element="Roles",
                    children=[role.to_element() for role in self._roles],
                    parent_id=self._web_id,
                    parent_web_id=self._web_id,
                    parent_web_url=self._web_url,
                )
            )
        if self._role_assignments:
            self._manifest.add(
                ManifestObject(
                    id=self._role_assignments_id,
                    object_type="DeploymentRoleAssignments",
                    element="RoleAssignments",
                    children=[assignment.to_element() for assignment in self._role_assignments],
                    parent_id=self._web_id,
                    parent_web_id=self._web_id,
                    parent_web_url=self._web_url,
                )
            )

    def _next_principal_id(self) -> int:
        self._principal_seq += 1
        return self._principal_seq

    def _guid(self, key: str) -> uuid.UUID:
        return uuid.uuid5(self._namespace, key)

    def _url(self, path: str) -> str:
        """The website-relative URL of an item (no leading slash, per the schema)."""
        return f"{self._list_url.strip('/')}/{path}"

    def _parent_id(self, path: str) -> str:
        """The parent folder's GUID (the library root when top-level)."""
        parent = PurePosixPath(path).parent
        if str(parent) in (".", ""):
            return self._root_folder_id
        return self.add_folder(str(parent))
