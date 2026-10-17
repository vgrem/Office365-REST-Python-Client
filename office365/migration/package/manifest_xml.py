"""SPO Migration API manifest package — XML models and serialization.

The SharePoint Migration API (``CreateMigrationJob`` /
``CreateMigrationJobEncrypted``) ingests content described by a set of XML
manifest files. This module models the **document-library subset** — webs, lists,
folders, files, and file versions — plus the small, fully-specified
``ExportSettings.xml`` / ``SystemData.xml`` / ``UserGroup.xml``.

The full ``DeploymentManifest`` schema has 100+ elements (content types, views,
web parts, list items, taxonomy, ...); only what a document-library migration
needs is modeled here. That subset is ingested end-to-end on a live tenant —
content, version history, authorship and permissions (see
``docs/migration.md``) — so the format below is exercised, not merely documented;
everything outside it is unmodeled rather than unverified.

References:
- https://learn.microsoft.com/en-us/sharepoint/dev/apis/migration-manifest
- https://learn.microsoft.com/en-us/sharepoint/dev/schema/deploymentmanifest-schema
"""

from __future__ import annotations

import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from datetime import date, datetime, timezone

from office365.migration.base import normalize_puid

MANIFEST_NS = "urn:deployment-manifest-schema"
SYSTEM_DATA_NS = "urn:deployment-systemdata-schema"
EXPORT_SETTINGS_NS = "urn:deployment-exportsettings-schema"
USER_GROUP_MAP_NS = "urn:deployment-usergroupmap-schema"
REQUIREMENTS_NS = "urn:deployment-requirements-schema"
ROOT_OBJECT_MAP_NS = "urn:deployment-rootobjectmap-schema"
LOOKUP_LIST_MAP_NS = "urn:deployment-lookuplistmap-schema"
VIEW_FORMS_LIST_NS = "urn:deployment-viewformlist-schema"

# ``ExportSettings/@SourceType`` accepted values.
SOURCE_TYPES = (
    "AmazonS3",
    "AzureStorage",
    "Box",
    "Dropbox",
    "Egnyte",
    "FileShare",
    "GoogleCloudStorage",
    "GoogleDrive",
    "MicrosoftStream",
    "OneDrive",
    "SharePointOnline",
    "SharePointOnPremServer",
    "Other",
)

__all__ = [
    "EXPORT_SETTINGS_NS",
    "LOOKUP_LIST_MAP_NS",
    "MANIFEST_NS",
    "REQUIREMENTS_NS",
    "ROOT_OBJECT_MAP_NS",
    "SOURCE_TYPES",
    "SYSTEM_DATA_NS",
    "USER_GROUP_MAP_NS",
    "VIEW_FORMS_LIST_NS",
    "Assignment",
    "DeploymentObject",
    "ExportSettings",
    "Group",
    "Manifest",
    "ManifestElement",
    "ManifestObject",
    "Role",
    "RoleAssignment",
    "RootObject",
    "RootObjectMap",
    "SharedWithEvent",
    "SystemData",
    "SystemObject",
    "User",
    "UserGroupMap",
    "empty_document",
]


def _q(ns: str, tag: str) -> str:
    """Qualify a tag with its XML namespace."""
    return f"{{{ns}}}{tag}"


def _str(value: object) -> str:
    """Render an attribute value (booleans as lowercase ``true``/``false``).

    ``datetime``/``date`` values are emitted as XML-Schema ``dateTime``/``date``
    (the Migration API rejects Python's ``str(datetime)`` space-separated form with
    a schema-validation fatal error), normalized to UTC.
    """
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, datetime):
        moment = value if value.tzinfo is not None else value.replace(tzinfo=timezone.utc)
        return moment.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    if isinstance(value, date):
        return value.isoformat()
    return str(value)


def _set(element: ET.Element, attributes: dict) -> None:
    """Set non-``None`` attributes on an element, in insertion order."""
    for name, value in attributes.items():
        if value is not None:
            element.set(name, _str(value))


def _indent(element: ET.Element, level: int = 0) -> None:
    """Indent element content (``ET.indent`` is Python 3.9+; this library supports 3.8)."""
    prefix = "\n" + "  " * level
    children = list(element)
    if children:
        if not (element.text or "").strip():
            element.text = prefix + "  "
        for child in children:
            _indent(child, level + 1)
        if not (children[-1].tail or "").strip():
            children[-1].tail = prefix
    if level and not (element.tail or "").strip():
        element.tail = prefix


def _serialize(root: ET.Element, ns: str) -> bytes:
    """Serialize a document with ``ns`` as the default namespace + XML declaration."""
    ET.register_namespace("", ns)
    _indent(root)
    return ET.tostring(root, encoding="utf-8", xml_declaration=True)


def empty_document(ns: str, root: str) -> bytes:
    """A document with a childless root element (the API fetches these files by name)."""
    return _serialize(ET.Element(_q(ns, root)), ns)


@dataclass
class ManifestElement:
    """A nested element inside an ``<SPObject>`` payload element.

    Generic recursion (name + attributes + children) covers ``<Versions>``,
    ``<Roles>``, ``<RoleAssignments>``, ``<SharedWithEvents>``, etc.
    """

    name: str
    attributes: dict = field(default_factory=dict)
    children: list["ManifestElement"] = field(default_factory=list)

    def to_etree(self, ns: str = MANIFEST_NS) -> ET.Element:
        element = ET.Element(_q(ns, self.name))
        _set(element, self.attributes)
        for child in self.children:
            element.append(child.to_etree(ns))
        return element


@dataclass
class ManifestObject:
    """A single ``<SPObject>`` entry in ``Manifest.xml``.

    ``attributes`` are rendered on the child element (``element``); ``children``
    render nested blocks (file versions, roles, role assignments, sharing).
    """

    id: str
    object_type: str  # SPFolder | SPDocumentLibrary | SPFile | ListItem | ...
    element: str  # child element name (Folder/DocumentLibrary/File/ListItem/...)
    attributes: dict = field(default_factory=dict)
    children: list[ManifestElement] = field(default_factory=list)
    parent_id: str | None = None
    parent_web_id: str | None = None
    parent_web_url: str | None = None
    url: str | None = None


@dataclass
class Manifest:
    """The ``Manifest.xml`` document — the content/structure catalog."""

    objects: list[ManifestObject] = field(default_factory=list)

    def add(self, obj: ManifestObject) -> "Manifest":
        self.objects.append(obj)
        return self

    def to_xml(self) -> bytes:
        root = ET.Element(_q(MANIFEST_NS, "SPObjects"))
        for obj in self.objects:
            sp = ET.SubElement(root, _q(MANIFEST_NS, "SPObject"))
            _set(
                sp,
                {
                    "Id": obj.id,
                    "ObjectType": obj.object_type,
                    "ParentId": obj.parent_id,
                    "ParentWebId": obj.parent_web_id,
                    "ParentWebUrl": obj.parent_web_url,
                    "Url": obj.url,
                },
            )
            element = ET.SubElement(sp, _q(MANIFEST_NS, obj.element))
            _set(element, obj.attributes)
            for child in obj.children:
                element.append(child.to_etree(MANIFEST_NS))
        return _serialize(root, MANIFEST_NS)


@dataclass
class Role:
    """A ``<Role>`` (permission level) inside a ``DeploymentRoles`` object."""

    id: str  # RoleId
    title: str
    perm_mask: str
    hidden: bool = False
    description: str | None = None
    role_order: str | None = None
    type: str | None = None

    def to_element(self) -> ManifestElement:
        return ManifestElement(
            "Role",
            {
                "RoleId": self.id,
                "Title": self.title,
                "Description": self.description,
                "PermMask": self.perm_mask,
                "Hidden": self.hidden,
                "RoleOrder": self.role_order,
                "Type": self.type,
            },
        )


@dataclass
class Assignment:
    """An ``<Assignment>`` — a role granted to a principal (a ``UserGroup`` id)."""

    role_id: str
    principal_id: int

    def to_element(self) -> ManifestElement:
        return ManifestElement("Assignment", {"RoleId": self.role_id, "PrincipalId": self.principal_id})


@dataclass
class RoleAssignment:
    """A ``<RoleAssignment>`` (an ACL scope) inside a ``DeploymentRoleAssignments`` object.

    ``object_id``/``object_url``/``object_type`` identify the secured object (a
    file/folder GUID), ``scope_id`` the scope it applies to; ``assignments`` map
    roles to principals from ``UserGroup.xml``.
    """

    object_id: str
    object_url: str
    object_type: str
    role_def_web_id: str
    role_def_web_url: str
    scope_id: str
    assignments: list[Assignment] = field(default_factory=list)
    anonymous_perm_mask: str = "0"

    def to_element(self) -> ManifestElement:
        return ManifestElement(
            "RoleAssignment",
            {
                "ScopeId": self.scope_id,
                "RoleDefWebId": self.role_def_web_id,
                "RoleDefWebUrl": self.role_def_web_url,
                "ObjectId": self.object_id,
                "ObjectType": self.object_type,
                "ObjectUrl": self.object_url,
                "AnonymousPermMask": self.anonymous_perm_mask,
            },
            children=[assignment.to_element() for assignment in self.assignments],
        )


@dataclass
class SharedWithEvent:
    """A ``<SharedWithEvent>`` — a "Shared with Me" occurrence on a list item."""

    shared_time: str
    sharing_initiator_id: int
    shared_by_id: int
    members: list[int] = field(default_factory=list)

    def to_element(self) -> ManifestElement:
        members = ManifestElement(
            "SharedWithMembers",
            children=[ManifestElement("SharedWithMember", {"SharedWithId": member}) for member in self.members],
        )
        return ManifestElement(
            "SharedWithEvent",
            {
                "SharedTime": self.shared_time,
                "SharingInitiatorId": self.sharing_initiator_id,
                "SharedById": self.shared_by_id,
            },
            children=[members],
        )


@dataclass
class RootObject:
    """A ``<RootObject>`` mapping in ``RootObjectMap.xml``."""

    id: str
    type: str  # Site | Web | Folder | List | ListItem | File
    parent_id: str | None = None
    web_url: str | None = None
    url: str | None = None
    is_dependency: bool = False


@dataclass
class RootObjectMap:
    """The ``RootObjectMap.xml`` document — dependent-object placement."""

    objects: list[RootObject] = field(default_factory=list)

    def to_xml(self) -> bytes:
        root = ET.Element(_q(ROOT_OBJECT_MAP_NS, "RootObjects"))
        for obj in self.objects:
            _set(
                ET.SubElement(root, _q(ROOT_OBJECT_MAP_NS, "RootObject")),
                {
                    "Id": obj.id,
                    "Type": obj.type,
                    "ParentId": obj.parent_id,
                    "WebUrl": obj.web_url,
                    "Url": obj.url,
                    "IsDependency": obj.is_dependency,
                },
            )
        return _serialize(root, ROOT_OBJECT_MAP_NS)


@dataclass
class DeploymentObject:
    """A ``<DeploymentObject>`` entry in ``ExportSettings.xml``."""

    id: str
    type: str  # List | Web | ...
    parent_id: str | None = None


@dataclass
class ExportSettings:
    """The required ``ExportSettings.xml`` document."""

    site_url: str
    source_type: str = "SharePointOnline"
    include_security: str = "None"
    file_location: str | None = None
    detailed_source: str | None = None
    export_objects: list[DeploymentObject] = field(default_factory=list)

    def to_xml(self) -> bytes:
        root = ET.Element(_q(EXPORT_SETTINGS_NS, "ExportSettings"))
        _set(
            root,
            {
                "SiteUrl": self.site_url,
                "FileLocation": self.file_location,
                "IncludeSecurity": self.include_security,
                "SourceType": self.source_type,
                "DetailedSource": self.detailed_source,
            },
        )
        if self.export_objects:
            objects = ET.SubElement(root, _q(EXPORT_SETTINGS_NS, "ExportObjects"))
            for obj in self.export_objects:
                _set(
                    ET.SubElement(objects, _q(EXPORT_SETTINGS_NS, "DeploymentObject")),
                    {"Id": obj.id, "Type": obj.type, "ParentId": obj.parent_id},
                )
        return _serialize(root, EXPORT_SETTINGS_NS)


@dataclass
class SystemObject:
    """A ``<SystemObject>`` entry (an immutable dependent object)."""

    id: str
    type: str  # Web | List | Folder
    url: str


@dataclass
class SystemData:
    """The required ``SystemData.xml`` document."""

    manifest_files: list[str] = field(default_factory=lambda: ["Manifest.xml"])
    system_objects: list[SystemObject] = field(default_factory=list)
    root_web_only_lists: list[str] = field(default_factory=list)
    version: str = "15.0.0.0"
    build: str = "16.0.3111.1200"
    database_version: int = 11552
    site_version: str = "15"

    def to_xml(self) -> bytes:
        root = ET.Element(_q(SYSTEM_DATA_NS, "SystemData"))
        _set(
            ET.SubElement(root, _q(SYSTEM_DATA_NS, "SchemaVersion")),
            {
                "Version": self.version,
                "Build": self.build,
                "DatabaseVersion": self.database_version,
                "SiteVersion": self.site_version,
            },
        )
        manifests = ET.SubElement(root, _q(SYSTEM_DATA_NS, "ManifestFiles"))
        for name in self.manifest_files:
            _set(ET.SubElement(manifests, _q(SYSTEM_DATA_NS, "ManifestFile")), {"Name": name})
        objects = ET.SubElement(root, _q(SYSTEM_DATA_NS, "SystemObjects"))
        for obj in self.system_objects:
            _set(
                ET.SubElement(objects, _q(SYSTEM_DATA_NS, "SystemObject")),
                {"Id": obj.id, "Type": obj.type, "Url": obj.url},
            )
        ET.SubElement(root, _q(SYSTEM_DATA_NS, "RootWebOnlyLists"))
        for url in self.root_web_only_lists:
            _set(ET.SubElement(root, _q(SYSTEM_DATA_NS, "RootWebOnlyLists")), {"Url": url})
        return _serialize(root, SYSTEM_DATA_NS)


@dataclass
class User:
    """A ``<User>`` entry in ``UserGroup.xml``.

    ``login`` must be a UPN-based login name (``i:0#.f|membership|user@contoso.com``)
    — non-UPN emails cause unexpected behavior in SharePoint Online.
    """

    id: int
    name: str
    login: str
    email: str | None = None
    is_domain_group: bool = False
    is_site_admin: bool = False
    system_id: str | None = None
    is_deleted: bool = False
    flags: int = 0


@dataclass
class Group:
    """A ``<Group>`` entry in ``UserGroup.xml``."""

    id: int
    name: str
    description: str | None = None
    owner: int | None = None
    owner_is_user: bool = True
    only_allow_members_view_membership: bool = True
    members: list[int] = field(default_factory=list)


@dataclass
class UserGroupMap:
    """The required ``UserGroup.xml`` document (entries are optional)."""

    users: list[User] = field(default_factory=list)
    groups: list[Group] = field(default_factory=list)

    def add_user(self, user: User) -> "UserGroupMap":
        self.users.append(user)
        return self

    def to_xml(self) -> bytes:
        root = ET.Element(_q(USER_GROUP_MAP_NS, "UserGroupMap"))
        users = ET.SubElement(root, _q(USER_GROUP_MAP_NS, "Users"))
        for user in self.users:
            _set(
                ET.SubElement(users, _q(USER_GROUP_MAP_NS, "User")),
                {
                    "Id": user.id,
                    "Name": user.name,
                    "Login": user.login,
                    "Email": user.email,
                    "IsDomainGroup": user.is_domain_group,
                    "IsSiteAdmin": user.is_site_admin,
                    # the service schema requires the attribute even when unknown
                    "SystemId": normalize_puid(user.system_id) or "",
                    "IsDeleted": user.is_deleted,
                },
            )
        groups = ET.SubElement(root, _q(USER_GROUP_MAP_NS, "Groups"))
        for group in self.groups:
            element = ET.SubElement(groups, _q(USER_GROUP_MAP_NS, "Group"))
            _set(
                element,
                {
                    "Id": group.id,
                    "Name": group.name,
                    "Description": group.description,
                    "Owner": group.owner,
                    "OwnerIsUser": group.owner_is_user,
                    "OnlyAllowMembersViewMembership": group.only_allow_members_view_membership,
                },
            )
            for member_id in group.members:
                _set(ET.SubElement(element, _q(USER_GROUP_MAP_NS, "Member")), {"UserId": member_id})
        return _serialize(root, USER_GROUP_MAP_NS)
