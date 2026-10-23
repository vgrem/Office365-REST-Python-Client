"""Structural tests for the SharePoint Migration API package builder (offline)."""

from __future__ import annotations

import base64
import xml.etree.ElementTree as ET

import pytest
from office365.migration.package import (
    EXPORT_SETTINGS_NS,
    LOOKUP_LIST_MAP_NS,
    MANIFEST_NS,
    REQUIREMENTS_NS,
    ROOT_OBJECT_MAP_NS,
    USER_GROUP_MAP_NS,
    VIEW_FORMS_LIST_NS,
    BlobStaging,
    FileSystemStaging,
    Group,
    PackageBuilder,
    SharedWithEvent,
    UserGroupMap,
)


def _q(ns: str, tag: str) -> str:
    return f"{{{ns}}}{tag}"


def _children(element, ns: str, tag: str):
    return element.findall(_q(ns, tag))


def test_manifest_renders_spobjects_with_file_and_versions():
    builder = PackageBuilder("https://contoso.sharepoint.com/sites/x", list_title="Documents")
    builder.add_file(
        "Reports/q1.docx",
        b"v2",
        version="2.0",
        versions=[("1.0", b"v1")],
        time_created="2020-01-01T00:00:00",
    )
    root = ET.fromstring(builder.build().manifest)

    assert root.tag == _q(MANIFEST_NS, "SPObjects")
    objects = _children(root, MANIFEST_NS, "SPObject")
    assert [o.get("ObjectType") for o in objects] == [
        "SPFolder",
        "SPDocumentLibrary",
        "SPFolder",
        "SPFile",
        "SPListItem",
    ]

    file_object = objects[-2]
    file_element = _children(file_object, MANIFEST_NS, "File")[0]
    assert file_element.get("Name") == "Reports/q1.docx"
    assert file_element.get("Url").endswith("Documents/Reports/q1.docx")
    assert file_element.get("FileValue") == file_object.get("Id")  # the content blob name
    assert file_element.get("Version") == "2.0"
    assert file_element.get("TimeCreated") == "2020-01-01T00:00:00"
    assert file_object.get("ParentId") == objects[-3].get("Id")  # the Reports folder

    version_rows = _children(_children(file_element, MANIFEST_NS, "Versions")[0], MANIFEST_NS, "File")
    # oldest first, current last (the API promotes the last <Versions> entry)
    assert [v.get("Version") for v in version_rows] == ["1.0", "2.0"]
    assert version_rows[-1].get("FileValue") == f"{file_object.get('Id')}.2.0"


def test_package_blobs_and_save(tmp_path):
    builder = PackageBuilder("https://contoso.sharepoint.com/sites/x", list_title="Documents")
    builder.add_folder("Empty")
    file_id = builder.add_file("a.txt", b"hi")
    package = builder.build()

    assert set(package.blobs()) == {
        "Manifest.xml",
        "ExportSettings.xml",
        "SystemData.xml",
        "UserGroup.xml",
        "Requirements.xml",
        "RootObjectMap.xml",
        "LookupListMap.xml",
        "ViewFormsList.xml",
    }

    written = package.save(tmp_path)
    assert (tmp_path / "manifest" / "Manifest.xml").exists()
    assert (tmp_path / "content" / file_id).read_bytes() == b"hi"  # blobs are GUID-named
    assert len(written) == len(package.blobs()) + len(package.content)


def test_optional_manifest_documents_are_emitted():
    package = PackageBuilder("https://contoso.sharepoint.com/sites/x", list_title="Documents").build()

    assert ET.fromstring(package.requirements).tag == _q(REQUIREMENTS_NS, "Requirements")
    assert ET.fromstring(package.lookup_list_map).tag == _q(LOOKUP_LIST_MAP_NS, "LookupLists")
    assert ET.fromstring(package.view_forms_list).tag == _q(VIEW_FORMS_LIST_NS, "ViewFormsList")

    root = ET.fromstring(package.root_object_map)
    assert root.tag == _q(ROOT_OBJECT_MAP_NS, "RootObjects")
    assert _children(root, ROOT_OBJECT_MAP_NS, "RootObject")[0].get("Type") == "List"


def test_builder_emits_role_assignments_and_user_system_id():
    builder = PackageBuilder("https://contoso.sharepoint.com/sites/x", list_title="Documents")
    uid = builder.add_user("i:0#.f|membership|jane@contoso.com", name="Jane")
    file_id = builder.add_file("a.txt", b"hi")
    builder.add_role_assignment(
        object_id=file_id,
        object_url="Documents/a.txt",
        object_type="1",
        role_def_web_id="web-1",
        role_def_web_url="/",
        assignments=[("1073741827", uid)],
    )
    package = builder.build()

    root = ET.fromstring(package.manifest)
    objects = {o.get("ObjectType"): o for o in _children(root, MANIFEST_NS, "SPObject")}
    assignments = _children(objects["DeploymentRoleAssignments"], MANIFEST_NS, "RoleAssignments")[0]
    role_assignment = _children(assignments, MANIFEST_NS, "RoleAssignment")[0]
    assert role_assignment.get("ObjectId") == file_id
    assert _children(role_assignment, MANIFEST_NS, "Assignment")[0].get("PrincipalId") == "1"

    # the service schema requires SystemId on every <User>
    user = _children(ET.fromstring(package.user_group_map), USER_GROUP_MAP_NS, "Users")[0][0]
    assert user.get("Login") == "i:0#.f|membership|jane@contoso.com"
    assert user.get("SystemId") == ""


def test_builder_emits_shared_with_events():
    builder = PackageBuilder("https://contoso.sharepoint.com/sites/x")
    builder.add_list_item(
        "Documents/a.txt",
        shared_with=[
            SharedWithEvent(shared_time="2024-01-01T00:00:00Z", sharing_initiator_id=1, shared_by_id=1, members=[2])
        ],
    )
    root = ET.fromstring(builder.build().manifest)
    item = next(o for o in _children(root, MANIFEST_NS, "SPObject") if o.get("ObjectType") == "SPListItem")

    events = _children(_children(item, MANIFEST_NS, "ListItem")[0], MANIFEST_NS, "SharedWithEvents")[0]
    event = _children(events, MANIFEST_NS, "SharedWithEvent")[0]
    assert event.get("SharedById") == "1"
    members = _children(_children(event, MANIFEST_NS, "SharedWithMembers")[0], MANIFEST_NS, "SharedWithMember")
    assert [m.get("SharedWithId") for m in members] == ["2"]


def test_add_role_requires_a_decimal_perm_mask():
    builder = PackageBuilder("https://contoso.sharepoint.com/sites/x")
    with pytest.raises(ValueError, match="decimal"):
        builder.add_role("1073000001", "Read", "0xb008431061")

    builder.add_role("1073000001", "Read", "756052856929")
    root = ET.fromstring(builder.build().manifest)
    roles_object = next(o for o in _children(root, MANIFEST_NS, "SPObject") if o.get("ObjectType") == "DeploymentRoles")
    role = _children(_children(roles_object, MANIFEST_NS, "Roles")[0], MANIFEST_NS, "Role")[0]
    assert role.get("Title") == "Read"
    assert role.get("PermMask") == "756052856929"


def test_add_user_requires_a_numeric_puid_system_id():
    builder = PackageBuilder("https://contoso.sharepoint.com/sites/x")
    with pytest.raises(ValueError, match="PUID"):
        builder.add_user("i:0i.t|00000003-0000-0ff1-ce00-000000000000|app@sharepoint", system_id="app@sharepoint")
    with pytest.raises(ValueError, match="PUID"):
        builder.add_user("i:0#.f|membership|jane@contoso.com", system_id="f310f81b-4066-4591-bcf3-e88804b12315")

    uid = builder.add_user("i:0#.f|membership|jane@contoso.com", system_id="1003200065102863")
    user = _children(ET.fromstring(builder.build().user_group_map), USER_GROUP_MAP_NS, "Users")[0][0]
    assert uid == 1
    assert user.get("SystemId") == "1003200065102863"


def test_object_id_and_item_url_and_include_security_helpers():
    builder = PackageBuilder("https://contoso.sharepoint.com/sites/x", list_title="Documents")
    file_id = builder.add_file("a/b.txt", b"hi")
    builder.add_folder("c")

    assert builder.object_id("a/b.txt") == file_id
    assert builder.object_id("a\\b.txt") == file_id  # separators are normalized
    assert builder.object_id("missing.txt") is None
    assert builder.item_url("a/b.txt").endswith("Documents/a/b.txt")

    builder.set_include_security("All")
    assert ET.fromstring(builder.build().export_settings).get("IncludeSecurity") == "All"


def test_export_settings_carries_source_type_and_list_object():
    builder = PackageBuilder(
        "https://contoso.sharepoint.com/sites/x",
        list_title="Shared Documents",
        source_type="FileShare",
        include_security="All",
    )
    root = ET.fromstring(builder.build().export_settings)

    assert root.tag == _q(EXPORT_SETTINGS_NS, "ExportSettings")
    assert root.get("SiteUrl") == "https://contoso.sharepoint.com/sites/x"
    assert root.get("SourceType") == "FileShare"
    assert root.get("IncludeSecurity") == "All"

    container = _children(root, EXPORT_SETTINGS_NS, "ExportObjects")[0]
    export_objects = _children(container, EXPORT_SETTINGS_NS, "DeploymentObject")
    assert [o.get("Type") for o in export_objects] == ["List"]


def test_user_group_map_renders_users():
    builder = PackageBuilder("https://contoso.sharepoint.com/sites/x")
    user_id = builder.add_user("i:0#.f|membership|jane@contoso.com", name="Jane", email="jane@contoso.com")
    assert user_id == 1

    root = ET.fromstring(builder.build().user_group_map)
    assert root.tag == _q(USER_GROUP_MAP_NS, "UserGroupMap")
    users = _children(_children(root, USER_GROUP_MAP_NS, "Users")[0], USER_GROUP_MAP_NS, "User")
    assert users[0].get("Id") == "1"
    assert users[0].get("Name") == "Jane"
    assert users[0].get("Login") == "i:0#.f|membership|jane@contoso.com"
    assert users[0].get("IsSiteAdmin") == "false"


def test_user_group_map_renders_group_members():
    model = UserGroupMap(groups=[Group(id=1, name="Team", members=[1, 2])])
    root = ET.fromstring(model.to_xml())
    group = _children(_children(root, USER_GROUP_MAP_NS, "Groups")[0], USER_GROUP_MAP_NS, "Group")[0]
    assert group.get("Name") == "Team"
    members = _children(group, USER_GROUP_MAP_NS, "Member")
    assert [m.get("UserId") for m in members] == ["1", "2"]


def test_file_system_staging_writes_both_containers(tmp_path):
    builder = PackageBuilder("https://contoso.sharepoint.com/sites/x")
    file_id = builder.add_file("a.txt", b"hi")
    package = builder.build()

    FileSystemStaging(tmp_path / "content", tmp_path / "manifest").stage(package)

    assert (tmp_path / "content" / file_id).read_bytes() == b"hi"
    assert (tmp_path / "manifest" / "Manifest.xml").exists()
    assert (tmp_path / "manifest" / "ExportSettings.xml").exists()


class _FakeBlob:
    def __init__(self) -> None:
        self.data = None
        self.metadata = None

    def upload_blob(self, data, overwrite=False, metadata=None):
        self.data = data
        self.metadata = metadata


def test_blob_staging_encrypts_blobs_with_an_iv_property():
    from office365.migration.package.crypto import decrypt, normalize_key

    key = base64.b64encode(bytes(range(32))).decode("ascii")
    staging = BlobStaging("https://a/content?sig=x", "https://a/manifest?sig=y", encryption_key=key)
    blob = _FakeBlob()

    staging._upload(blob, b"hello world")  # noqa: SLF001

    assert blob.data != b"hello world"
    assert decrypt(blob.data, normalize_key(key), blob.metadata["IV"]) == b"hello world"


class _BlobProps:
    def __init__(self, metadata):
        self.metadata = metadata


class _PropsBlob:
    def __init__(self, metadata):
        self._metadata = metadata

    def get_blob_properties(self):
        return _BlobProps(self._metadata)


def test_blob_iv_reads_case_insensitively():
    from office365.migration.package.staging import _blob_iv

    assert _blob_iv(_PropsBlob({"iv": "abc"})) == "abc"
    assert _blob_iv(_PropsBlob({"IV": "xyz"})) == "xyz"
    assert _blob_iv(_PropsBlob({})) is None
