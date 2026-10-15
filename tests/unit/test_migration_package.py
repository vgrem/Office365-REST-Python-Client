"""Structural tests for the SharePoint Migration API package builder (offline)."""

from __future__ import annotations

import base64
import importlib.util
import xml.etree.ElementTree as ET
from datetime import datetime, timezone

import pytest
from office365.migration.package import (
    EXPORT_SETTINGS_NS,
    LOOKUP_LIST_MAP_NS,
    MANIFEST_NS,
    REQUIREMENTS_NS,
    ROOT_OBJECT_MAP_NS,
    SYSTEM_DATA_NS,
    USER_GROUP_MAP_NS,
    VIEW_FORMS_LIST_NS,
    AzureBlobStaging,
    BlobStaging,
    FileSystemStaging,
    Group,
    Package,
    PackageBuilder,
    SharedWithEvent,
    UserGroupMap,
    create_staging,
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


def test_manifest_normalizes_datetime_attributes_to_xsd_utc():
    builder = PackageBuilder("https://contoso.sharepoint.com/sites/x", list_title="Documents")
    builder.add_file(
        "doc.txt",
        b"v1",
        time_created=datetime(2020, 1, 2, 3, 4, 5),  # naive → assume UTC
        time_last_modified=datetime(2020, 1, 2, 5, 4, 5, tzinfo=timezone.utc),
    )
    root = ET.fromstring(builder.build().manifest)
    file_object = _children(root, MANIFEST_NS, "SPObject")[-2]
    file_element = _children(file_object, MANIFEST_NS, "File")[0]

    # The Migration API rejects ``str(datetime)`` (space-separated); must be XSD dateTime.
    assert file_element.get("TimeCreated") == "2020-01-02T03:04:05Z"
    assert file_element.get("TimeLastModified") == "2020-01-02T05:04:05Z"


def test_builder_ids_are_deterministic():
    def build() -> bytes:
        builder = PackageBuilder("https://contoso.sharepoint.com/sites/x")
        builder.add_file("a/b.txt", b"hi")
        return builder.build().manifest

    assert build() == build()


def test_builder_creates_missing_parent_folders():
    builder = PackageBuilder("https://contoso.sharepoint.com/sites/x")
    builder.add_file("a/b/c.txt", b"hi")
    root = ET.fromstring(builder.build().manifest)
    objects = _children(root, MANIFEST_NS, "SPObject")

    assert [o.get("ObjectType") for o in objects] == [
        "SPFolder",
        "SPDocumentLibrary",
        "SPFolder",
        "SPFolder",
        "SPFile",
        "SPListItem",
    ]
    folders = [_children(o, MANIFEST_NS, "Folder")[0] for o in objects if o.get("ObjectType") == "SPFolder"]
    assert [f.get("Name") for f in folders] == ["Documents", "a", "a/b"]  # the library root, then a and a/b


def test_content_blobs_are_named_after_the_file_guid():
    builder = PackageBuilder("https://contoso.sharepoint.com/sites/x")
    file_id = builder.add_file("f.txt", b"current", version="2.0", versions=[("1.0", b"old")])
    package = builder.build()

    assert set(package.content) == {file_id, f"{file_id}.1.0", f"{file_id}.2.0"}
    assert package.content[file_id] == b"current"
    assert package.content[f"{file_id}.1.0"] == b"old"
    assert package.content[f"{file_id}.2.0"] == b"current"


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


def test_system_data_lists_manifests_and_system_objects():
    builder = PackageBuilder("https://contoso.sharepoint.com/sites/x")
    root = ET.fromstring(builder.build().system_data)

    assert root.tag == _q(SYSTEM_DATA_NS, "SystemData")
    schema = _children(root, SYSTEM_DATA_NS, "SchemaVersion")[0]
    assert schema.get("Version") == "15.0.0.0"
    assert schema.get("SiteVersion") == "15"

    manifest_files = _children(_children(root, SYSTEM_DATA_NS, "ManifestFiles")[0], SYSTEM_DATA_NS, "ManifestFile")
    assert [m.get("Name") for m in manifest_files] == ["Manifest.xml"]

    system_objects = _children(_children(root, SYSTEM_DATA_NS, "SystemObjects")[0], SYSTEM_DATA_NS, "SystemObject")
    assert [o.get("Type") for o in system_objects] == ["Web", "List"]


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


def test_azure_blob_staging_is_an_alias_of_blob_staging():
    assert AzureBlobStaging is BlobStaging


def test_blob_staging_rejects_the_same_container():
    with pytest.raises(ValueError, match="differ"):
        BlobStaging("https://acct.blob.core.windows.net/c?sig=x", "https://acct.blob.core.windows.net/c?sig=x")


def test_blob_staging_requires_the_azure_extra():
    try:
        importlib.import_module("azure.storage.blob")
    except ImportError:
        pass
    else:
        pytest.skip("azure extra installed")
    staging = BlobStaging("https://a/content?sig=x", "https://a/manifest?sig=y")
    with pytest.raises(ImportError, match="azure"):
        staging.stage(Package(manifest=b"", export_settings=b"", system_data=b"", user_group_map=b""))


def test_create_staging_selects_blob_staging_for_azure_hosts():
    staging = create_staging(
        "https://acct.blob.core.windows.net/content?sig=x",
        "https://acct.blob.core.windows.net/manifest?sig=y",
    )
    assert isinstance(staging, BlobStaging)

    gov = create_staging(
        "https://acct.blob.core.usgovcloudapi.net/content?sig=x",
        "https://acct.blob.core.usgovcloudapi.net/manifest?sig=y",
    )
    assert isinstance(gov, BlobStaging)


def test_create_staging_rejects_unknown_hosts():
    with pytest.raises(ValueError, match="unsupported staging container host"):
        create_staging("https://bucket.s3.amazonaws.com/content", "https://bucket.s3.amazonaws.com/manifest")


class _FakeBlob:
    def __init__(self) -> None:
        self.data = None
        self.metadata = None

    def upload_blob(self, data, overwrite=False, metadata=None):
        self.data = data
        self.metadata = metadata


def test_create_staging_forwards_the_encryption_key():
    staging = create_staging(
        "https://acct.blob.core.windows.net/content?sig=x",
        "https://acct.blob.core.windows.net/manifest?sig=y",
        encryption_key=base64.b64encode(bytes(range(32))).decode("ascii"),
    )
    assert isinstance(staging, BlobStaging)
    assert staging._key == bytes(range(32))  # noqa: SLF001


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


def test_blob_staging_uploads_plaintext_without_a_key():
    staging = BlobStaging("https://a/content?sig=x", "https://a/manifest?sig=y")
    blob = _FakeBlob()

    staging._upload(blob, b"hello world")  # noqa: SLF001

    assert blob.data == b"hello world"
    assert blob.metadata is None
