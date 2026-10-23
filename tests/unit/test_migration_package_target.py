"""Tests for the server-side migration package target (offline)."""

from __future__ import annotations

import json
import xml.etree.ElementTree as ET

from office365.migration.base import MigrationItem, MigrationOptions, PermissionEntry, Principal
from office365.migration.package import FileSystemStaging
from office365.migration.sharepoint import package_target
from office365.migration.sharepoint.package_target import SharePointPackageTarget
from office365.migration.sharepoint.structure import ListStructure


class _SPList:
    """The target library object ``provision_list_structure`` would provision into."""

    title = "Documents"


def _structure():
    return ListStructure(title="Documents", base_template=101, base_type=1)


class _Result:
    def __init__(self, value):
        self.value = value

    def execute_query(self):
        return self


class _Progress:
    def __init__(self, logs, next_token):
        self.Logs = logs
        self.NextToken = next_token


class _Site:
    url = "https://contoso.sharepoint.com/sites/x"

    def __init__(self):
        self.calls: list = []

    def create_migration_ingestion_job(self, **kwargs):
        self.calls.append(("ingestion", kwargs))
        return _Result("job-1")

    def create_migration_job_encrypted(self, **kwargs):
        self.calls.append(("encrypted", kwargs))
        return _Result("job-2")

    def get_migration_job_progress(self, job_id, next_token):
        self.calls.append(("progress", job_id, next_token))
        logs = [json.dumps({"Event": "JobEnd", "TotalErrors": "0"})]
        return _Result(_Progress(logs, next_token))


def _target(tmp_path, site=None, **kwargs):
    return SharePointPackageTarget(
        site or _Site(),
        "web-id",
        content_uri="https://a/content?sig=x",
        manifest_uri="https://a/manifest?sig=y",
        staging=FileSystemStaging(tmp_path / "content", tmp_path / "manifest"),
        **kwargs,
    )


def test_write_accumulates_files_and_folders(tmp_path):
    target = _target(tmp_path)
    target.write(MigrationItem("src/a", "Folder/", item_type="folder"), b"")
    target.write(MigrationItem("src/b", "Folder/b.txt", item_type="file", created="2020-01-01T00:00:00"), b"hi")

    package = target.build()
    root = ET.fromstring(package.manifest)
    assert [o.get("ObjectType") for o in root] == [
        "SPFolder",
        "SPDocumentLibrary",
        "SPFolder",
        "SPFile",
        "SPListItem",
    ]
    assert len(package.content) == 1


def test_commit_stages_and_submits(tmp_path):
    site = _Site()
    target = _target(tmp_path, site=site, azure_queue_report_uri="https://a/queue?sig=z")
    target.write(MigrationItem("src/b.txt", "b.txt", item_type="file"), b"hi")

    target.commit()

    assert target.job_id == "job-1"
    kind, kwargs = site.calls[0]
    assert kind == "ingestion"
    assert kwargs["g_web_id"] == "web-id"
    assert kwargs["azure_container_source_uri"] == "https://a/content?sig=x"
    assert kwargs["azure_container_manifest_uri"] == "https://a/manifest?sig=y"
    assert kwargs["azure_queue_report_uri"] == "https://a/queue?sig=z"
    assert (tmp_path / "manifest" / "Manifest.xml").exists()
    assert list((tmp_path / "content").iterdir())  # a content blob was staged


def test_commit_uses_encrypted_submit_with_a_key(tmp_path):
    site = _Site()
    target = _target(tmp_path, site=site, encryption_key=b"secret")
    target.write(MigrationItem("src/b.txt", "b.txt", item_type="file"), b"hi")

    target.commit()

    assert target.job_id == "job-2"
    kind, kwargs = site.calls[0]
    assert kind == "encrypted"
    assert kwargs["aes256_cbc_key"] == b"secret"


def test_configure_replays_a_captured_structure_once(tmp_path, monkeypatch):
    # The manifest carries a file's list item, not the library's columns: a snapshot
    # handed in has to be applied *before* the job runs, and only once even though
    # both ``configure`` and ``commit`` ask for it.
    calls: list = []

    def fake_provision(sp_list, structure, **kwargs):
        calls.append((sp_list, structure, kwargs))
        return ["view 'All Items' was created without LinkTitle"]

    monkeypatch.setattr(package_target, "provision_list_structure", fake_provision)
    sp_list, structure = _SPList(), _structure()
    target = _target(tmp_path, sp_list=sp_list, structure=structure)
    target.write(MigrationItem("src/b.txt", "b.txt", item_type="file"), b"hi")

    target.configure(MigrationOptions())
    target.commit()

    assert [call[0] for call in calls] == [sp_list]
    assert calls[0][1] is structure
    assert target.warnings == ["view 'All Items' was created without LinkTitle"]


def test_diagnose_falls_back_to_events_without_a_log(tmp_path):
    target = _target(tmp_path)  # FileSystemStaging has no manifest log
    target.job_id = "job-1"

    assert target.diagnose() == ["· JobEnd:"]


def test_write_registers_author_and_editor_in_usergroup(tmp_path):
    target = _target(tmp_path)
    item = MigrationItem(
        "src/b.txt",
        "b.txt",
        item_type="file",
        author=Principal("i:0#.f|membership|a@contoso.com", "1003200065102863", "Alice", "a@contoso.com"),
        editor=Principal("i:0#.f|membership|b@contoso.com", "2003200065102863", "Bob"),
    )

    target.write(item, b"hi")
    package = target.build()

    file_object = next(o for o in ET.fromstring(package.manifest) if o.get("ObjectType") == "SPFile")
    file_element = file_object.find("{urn:deployment-manifest-schema}File")
    assert file_element is not None
    assert file_element.get("Author") == "1"
    assert file_element.get("ModifiedBy") == "2"
    user_group = package.user_group_map.decode()
    assert 'SystemId="1003200065102863"' in user_group
    assert "i:0#.f|membership|a@contoso.com" in user_group


def test_apply_permissions_emits_role_and_assignment(tmp_path):
    target = _target(tmp_path)
    target.configure(MigrationOptions(preserve_permissions=True))
    item = MigrationItem("src/b.txt", "b.txt", item_type="file")
    target.write(item, b"hi")
    target.apply_permissions(
        item,
        [
            PermissionEntry(
                principal_name="i:0#.f|membership|a@contoso.com",
                roles=["Read"],
                system_id="1003200065102863",
                role_masks={"Read": "756052856929"},
            )
        ],
    )

    package = target.build()
    root = ET.fromstring(package.manifest)
    object_types = [o.get("ObjectType") for o in root]
    assert "DeploymentRoles" in object_types
    assert "DeploymentRoleAssignments" in object_types
    xml = package.manifest.decode()
    assert 'Title="Read"' in xml
    assert 'PermMask="756052856929"' in xml
    assert 'ObjectType="2"' in xml  # targets the file, not its parent web


def test_apply_permissions_skips_principal_without_a_puid(tmp_path):
    target = _target(tmp_path)
    item = MigrationItem("src/b.txt", "b.txt", item_type="file")
    target.write(item, b"hi")

    target.apply_permissions(item, [PermissionEntry(principal_name="Team Owners", roles=["Read"])])

    assert any("PUID" in w for w in target.warnings)
    assert b"DeploymentRoleAssignments" not in target.build().manifest


def test_apply_permissions_grants_a_sharepoint_group_by_title(tmp_path):
    target = _target(tmp_path)
    target.configure(MigrationOptions(preserve_permissions=True))
    item = MigrationItem("src/b.txt", "b.txt", item_type="file")
    target.write(item, b"hi")
    target.apply_permissions(
        item,
        [
            PermissionEntry(
                principal_name="default:members",
                roles=["Read"],
                display_name="Test site Members",
                role_masks={"Read": "756052856929"},
                principal_type="group",
                owner=Principal("i:0#.f|membership|a@contoso.com", "1003200065102863", "Alice"),
            )
        ],
    )

    package = target.build()
    group_map = ET.fromstring(package.user_group_map)
    groups = [element for element in group_map.iter() if element.tag.endswith("}Group")]
    assert [group.get("Name") for group in groups] == ["Test site Members"]  # its title, not the normalized name
    users = [element for element in group_map.iter() if element.tag.endswith("}User")]
    assert [user.get("SystemId") for user in users] == ["1003200065102863"]  # the owner's PUID
    assert groups[0].get("Owner") == users[0].get("Id")
    assert groups[0].get("OwnerIsUser") == "true"
    assert f'PrincipalId="{groups[0].get("Id")}"' in package.manifest.decode()
    assert target.warnings == []


def test_apply_permissions_writes_a_group_self_owned_when_its_owner_is_unknown(tmp_path):
    target = _target(tmp_path)
    item = MigrationItem("src/b.txt", "b.txt", item_type="file")
    target.write(item, b"hi")
    target.apply_permissions(
        item,
        [
            PermissionEntry(
                principal_name="Team Owners",
                roles=["Read"],
                display_name="Team Owners",
                role_masks={"Read": "756052856929"},
                principal_type="group",
            )
        ],
    )

    # UserGroup.xml rejects a <Group> without an Owner, and that fails the whole job;
    # a group may own itself (a tenant's default Owners group does), so the grant stays.
    package = target.build()
    group_map = ET.fromstring(package.user_group_map)
    groups = [element for element in group_map.iter() if element.tag.endswith("}Group")]
    assert [group.get("Name") for group in groups] == ["Team Owners"]
    assert groups[0].get("Owner") == groups[0].get("Id")
    assert groups[0].get("OwnerIsUser") == "false"
    assert 'PrincipalId="1"' in package.manifest.decode()
    assert any("written self-owned" in warning for warning in target.warnings)


def test_package_target_reports_full_fidelity_when_requested(tmp_path):
    from office365.migration.fidelity import describe_fidelity

    class _Source:
        def read_permissions(self, item):
            return []

        def read_version_history(self, item):
            return []

    options = MigrationOptions(preserve_timestamps=True, preserve_permissions=True, preserve_versions=True)
    report = describe_fidelity(_Source(), _target(tmp_path), options)

    assert sorted(report.preserved) == ["permissions", "timestamps", "versions"]
    assert report.unsupported == []


def test_apply_permissions_points_a_group_at_its_owner_group(tmp_path):
    # Live shape: Visitors is owned by Owners, which owns itself.
    target = _target(tmp_path)
    item = MigrationItem("src/b.txt", "b.txt", item_type="file")
    target.write(item, b"hi")
    target.apply_permissions(
        item,
        [
            PermissionEntry(
                principal_name="default:Visitors",
                roles=["Read"],
                display_name="Test site Visitors",
                role_masks={"Read": "756052856929"},
                principal_type="group",
                owner_groups=["Test site Owners"],
            )
        ],
    )

    group_map = ET.fromstring(target.build().user_group_map)
    groups = {
        element.get("Name"): (element.get("Id"), element.get("Owner"), element.get("OwnerIsUser"))
        for element in group_map.iter()
        if element.tag.endswith("}Group")
    }
    visitors, owners = groups["Test site Visitors"], groups["Test site Owners"]
    assert visitors[1] == owners[0]  # Visitors' owner is the Owners group
    assert visitors[2] == "false"  # ... which is a group, not a user
    assert owners[1] == owners[0]  # the Owners group owns itself, as on the source
    assert owners[2] == "false"
    assert target.warnings == []
