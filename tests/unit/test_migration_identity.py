"""Unit tests for the identity map (authorship/ACL principal resolution)."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from office365.migration import IdentityMap, MigrationOptions
from office365.migration.base import MigrationItem, PermissionEntry, Principal
from office365.migration.checkpoint import Checkpoint
from office365.migration.report import build_report
from office365.migration.runner import MigrationRunner

CLAIMS = "i:0#.f|membership|"
ANNA = CLAIMS + "anna@contoso.com"


def _item(author: Principal | None = None, editor: Principal | None = None) -> MigrationItem:
    return MigrationItem(source_path="a.txt", dest_path="a.txt", author=author, editor=editor)


class TestPolicies(unittest.TestCase):
    def test_fallback_owner_substitutes_a_miss(self) -> None:
        identity_map = IdentityMap([], unmapped_policy="fallback-owner", fallback_owner="migration@fabrikam.com")

        resolved = identity_map.resolve("stranger@elsewhere.example")

        assert resolved is not None
        assert resolved.login_name == "migration@fabrikam.com"
        assert identity_map.unmapped == ["stranger@elsewhere.example"]


class TestPermissions(unittest.TestCase):
    def test_a_mapped_grant_carries_the_target_system_id(self) -> None:
        identity_map = IdentityMap([("anna@contoso.com", "anna@fabrikam.com", "puid-target")])
        entries = [PermissionEntry(principal_name=ANNA, roles=["Read"], system_id="puid-source")]

        resolved = identity_map.resolve_permissions(entries)

        assert len(resolved) == 1
        assert resolved[0].principal_name == "anna@fabrikam.com"
        # The source PUID identifies a user in another tenant: carrying it would emit
        # an unresolvable SystemId in UserGroup.xml.
        assert resolved[0].system_id == "puid-target"
        assert resolved[0].roles == ["Read"]


class TestFromCsv(unittest.TestCase):
    def _write(self, text: str) -> Path:
        handle = tempfile.NamedTemporaryFile("w", suffix=".csv", delete=False, encoding="utf-8")
        handle.write(text)
        handle.close()
        self.addCleanup(Path(handle.name).unlink)
        return Path(handle.name)

    def test_a_file_without_the_required_columns_is_rejected(self) -> None:
        path = self._write("login,roles\r\nanna@contoso.com,Read\r\n")

        with self.assertRaises(ValueError) as raised:
            IdentityMap.from_csv(path)

        assert "source" in str(raised.exception)


class _RecordingSource:
    """A source whose items always carry a source-tenant author/editor."""

    def __init__(self, author: Principal, permissions: list[PermissionEntry] | None = None) -> None:
        self._author = author
        self._permissions = permissions or []
        self.reads: list[str] = []

    def read(self, item: MigrationItem) -> bytes:
        self.reads.append(item.dest_path)
        return b"payload"

    def read_permissions(self, item: MigrationItem) -> list[PermissionEntry]:
        return list(self._permissions)

    def checksum(self, item: MigrationItem) -> str:
        return "checksum"

    def supports_attachments(self) -> bool:  # pragma: no cover - not consulted here
        return False


class _RecordingTarget:
    """A target that records the principals it was asked to apply."""

    def __init__(self) -> None:
        self.authors: list[Principal | None] = []
        self.permissions: list[list[PermissionEntry]] = []

    def exists(self, item: MigrationItem) -> bool:
        return False

    def write(self, item: MigrationItem, payload: object) -> None:
        self.authors.append(item.author)

    def checksum(self, item: MigrationItem) -> str:
        return "checksum"

    def list_paths(self) -> list[str]:  # pragma: no cover - not consulted here
        return []

    def apply_authorship(self, item: MigrationItem) -> None:
        self.authors.append(item.author)

    def apply_permissions(self, item: MigrationItem, permissions: list[PermissionEntry]) -> None:
        self.permissions.append(list(permissions))

    def apply_timestamps(self, item: MigrationItem) -> None:
        pass


class TestRunnerWiring(unittest.TestCase):
    def _run(self, options: MigrationOptions) -> tuple[_RecordingTarget, list[MigrationItem]]:
        source = _RecordingSource(Principal(ANNA), [PermissionEntry(principal_name=ANNA, roles=["Read"])])
        target = _RecordingTarget()
        item = _item(Principal(ANNA), Principal(ANNA))
        runner = MigrationRunner()
        runner.run(source, target, [item], options, Checkpoint.create("run"))
        return target, [item]

    def test_the_engine_maps_authorship_and_acl(self) -> None:
        identity_map = IdentityMap([(ANNA, "anna@fabrikam.com")])

        target, _ = self._run(
            MigrationOptions(preserve_authorship=True, preserve_permissions=True, identity_map=identity_map)
        )

        assert target.authors[0] is not None
        assert target.authors[0].login_name == "anna@fabrikam.com"
        assert target.permissions[0][0].principal_name == "anna@fabrikam.com"

    def test_skipped_principals_are_reported_not_silently_kept(self) -> None:
        identity_map = IdentityMap([("someone-else@contoso.com", "someone@fabrikam.com")])

        target, items = self._run(
            MigrationOptions(preserve_authorship=True, preserve_permissions=True, identity_map=identity_map)
        )

        assert items[0].author is None
        assert target.authors[0] is None
        assert target.permissions == []  # the unmapped ACL entry is not applied
        assert identity_map.unmapped == [ANNA]


class TestSettingsAndReport(unittest.TestCase):
    def test_the_summary_row_reports_the_unmapped_principals(self) -> None:
        identity_map = IdentityMap([])
        identity_map.resolve(ANNA)
        job = _Job(options=MigrationOptions(identity_map=identity_map))

        summary = build_report(job).summary[0]

        assert summary["identity_unmapped"] == 1
        assert summary["identity_unmapped_principals"] == ANNA
        assert summary["identity_policy"] == "skip"


class _Job:
    """The slice of ``MigrationJob`` that ``build_report`` reads."""

    def __init__(self, options: MigrationOptions) -> None:
        from office365.migration.base import MigrationPhase, MigrationStats
        from office365.migration.manifest import Manifest

        self.options = options
        self.stats = MigrationStats()
        self.manifest = Manifest()
        self.checkpoint = Checkpoint.create("run")
        self.source_label = "source"
        self.target_label = "target"
        self.started_at = None
        self.finished_at = None
        self.duration = None
        self.phase = MigrationPhase.RUNNING

    def fidelity(self):
        from office365.migration.fidelity import FidelityReport

        return FidelityReport()
