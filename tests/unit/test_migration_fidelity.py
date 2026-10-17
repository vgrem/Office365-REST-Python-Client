"""Tests for migration metadata capture and honest fidelity guards."""

from __future__ import annotations

import datetime

import pytest
from office365.migration.adapters.filesystem import FileSystemSource
from office365.migration.base import (
    MigrationItem,
    MigrationOptions,
    PermissionEntry,
    Principal,
    item_from_dict,
    item_to_dict,
)
from office365.migration.runner import _assert_fidelity_supported
from office365.runtime.converters.scalars import iso_or_none


def test_iso_or_none():
    assert iso_or_none(None) is None
    assert iso_or_none(datetime.datetime.min) is None  # SharePoint "not loaded" sentinel
    assert iso_or_none(datetime.datetime(2020, 1, 2, 3, 4, 5)) == "2020-01-02T03:04:05"


def test_migration_item_metadata_round_trips():
    item = MigrationItem(
        "src",
        "dst",
        created="2020-01-01T00:00:00",
        modified="2021-01-01T00:00:00",
        author_id=1,
        editor_id=2,
    )

    restored = item_from_dict(item_to_dict(item))

    assert restored.created == "2020-01-01T00:00:00"
    assert restored.modified == "2021-01-01T00:00:00"
    assert restored.author_id == 1
    assert restored.editor_id == 2  # noqa: PLR2004


def test_migration_item_principal_round_trips_json_safely():
    import json

    item = MigrationItem(
        "src",
        "dst",
        author=Principal("i:0#.f|membership|a@contoso.com", "1003200065102863", "Alice", "a@contoso.com"),
        editor=Principal("i:0#.f|membership|b@contoso.com", "2003200065102863"),
    )

    data = item_to_dict(item)
    json.dumps(data)  # nested principals must be JSON-safe
    restored = item_from_dict(data)

    assert restored.author == Principal("i:0#.f|membership|a@contoso.com", "1003200065102863", "Alice", "a@contoso.com")
    assert restored.editor is not None and restored.editor.system_id == "2003200065102863"


def test_preserve_versions_always_needs_the_server_side_api():
    with pytest.raises(NotImplementedError, match="preserve_versions"):
        _assert_fidelity_supported(MigrationOptions(preserve_versions=True), _Source([]), _Target())


def test_fidelity_flags_require_adapter_support():
    source, target = _Source([]), _Target()
    with pytest.raises(NotImplementedError, match="preserve_timestamps"):
        _assert_fidelity_supported(MigrationOptions(preserve_timestamps=True), source, target)
    with pytest.raises(NotImplementedError, match="preserve_permissions"):
        _assert_fidelity_supported(MigrationOptions(preserve_permissions=True), source, target)

    _assert_fidelity_supported(MigrationOptions(), source, target)  # defaults are honest no-ops


def test_fidelity_flags_pass_when_adapters_support_them():
    source, target = _FidelitySource([]), _FidelityTarget()
    _assert_fidelity_supported(MigrationOptions(preserve_timestamps=True, preserve_permissions=True), source, target)


def test_runner_applies_fidelity_hooks_after_write():
    from office365.migration.checkpoint import Checkpoint
    from office365.migration.runner import MigrationRunner

    item = MigrationItem("s", "a", created="2020-01-01T00:00:00+00:00", modified="2021-01-01T00:00:00+00:00")
    source, target = _FidelitySource([item]), _FidelityTarget()

    MigrationRunner().run(
        source,
        target,
        source.list_items(),
        MigrationOptions(preserve_timestamps=True, preserve_permissions=True),
        Checkpoint.create(),
    )

    assert target.written == ["a"]
    assert target.timestamps == ["a"]
    assert target.permissions[0][0] == "a"
    assert target.permissions[0][1][0].principal_name == "user@contoso.com"


def test_sp_timestamp_normalizes_offsets_for_sharepoint():
    from office365.migration.sharepoint.adapters import _sp_local_timestamp, _sp_utc_timestamp

    assert _sp_utc_timestamp(None) is None
    assert _sp_utc_timestamp("") is None
    # List items honor the ``...Z`` UTC form.
    assert _sp_utc_timestamp("2021-01-01T00:00:00+00:00") == "2021-01-01T00:00:00Z"
    assert _sp_utc_timestamp("2021-01-01T00:00:00") == "2021-01-01T00:00:00Z"
    # Document items take an already-converted web-local wall-clock.
    assert _sp_local_timestamp(None) is None
    assert _sp_local_timestamp(datetime.datetime(2021, 1, 1, 8, 0, 0)) == "2021-01-01 08:00:00"


def test_filesystem_source_captures_timestamps(tmp_path):
    (tmp_path / "a.txt").write_text("hi", encoding="utf-8")

    items = FileSystemSource(tmp_path).list_items()

    assert items[0].modified
    assert items[0].created


def test_watermark_skips_stale_and_advances():
    from office365.migration.checkpoint import Checkpoint
    from office365.migration.runner import _Watermark

    checkpoint = Checkpoint.create()
    watermark = _Watermark(checkpoint)
    assert watermark.value is None

    old = MigrationItem("s", "d1", modified="2020-01-01T00:00:00")
    new = MigrationItem("s", "d2", modified="2021-01-01T00:00:00")

    assert not watermark.is_stale(old)
    watermark.advance(old)
    assert checkpoint.source_watermark == "2020-01-01T00:00:00"
    assert watermark.is_stale(old)  # at the watermark -> already migrated
    assert not watermark.is_stale(new)

    watermark.advance(new)
    assert checkpoint.source_watermark == "2021-01-01T00:00:00"


class _Source:
    def __init__(self, items: list[MigrationItem]) -> None:
        self._items = items

    def list_items(self, progress=None):
        return list(self._items)

    def read(self, item):
        return b"data"

    def checksum(self, item):
        return ""

    def close(self):
        pass


class _Target:
    def __init__(self) -> None:
        self.written: list[str] = []

    def exists(self, item):
        return False

    def write(self, item, payload):
        self.written.append(item.dest_path)

    def list_paths(self):
        return list(self.written)

    def checksum(self, item):
        return ""

    def close(self):
        pass


class _FidelitySource(_Source):
    def read_permissions(self, item):
        return [PermissionEntry(principal_name="user@contoso.com", roles=["Read"])]


class _FidelityTarget(_Target):
    def __init__(self) -> None:
        super().__init__()
        self.timestamps: list[str] = []
        self.permissions: list = []

    def apply_timestamps(self, item):
        self.timestamps.append(item.dest_path)

    def apply_permissions(self, item, permissions):
        self.permissions.append((item.dest_path, permissions))


def test_incremental_run_uses_watermark():
    from office365.migration.checkpoint import Checkpoint
    from office365.migration.runner import MigrationRunner

    source = _Source([MigrationItem("s", "a", modified="2020-01-01T00:00:00")])
    target = _Target()
    runner = MigrationRunner()

    first = Checkpoint.create()
    runner.run(source, target, source.list_items(), MigrationOptions(incremental=True), first)
    assert target.written == ["a"]
    assert first.source_watermark == "2020-01-01T00:00:00"

    # a fresh checkpoint carrying the watermark skips the unchanged item
    second = Checkpoint.create()
    second.source_watermark = first.source_watermark
    runner.run(source, target, source.list_items(), MigrationOptions(incremental=True), second)
    assert target.written == ["a"]  # nothing re-written

    # a newer item is migrated and advances the watermark
    source._items.append(MigrationItem("s", "b", modified="2021-01-01T00:00:00"))
    runner.run(source, target, source.list_items(), MigrationOptions(incremental=True), second)
    assert target.written == ["a", "b"]
    assert second.source_watermark == "2021-01-01T00:00:00"


def test_version_sort_key_orders_labels():
    from office365.migration.sharepoint.adapters import _version_sort_key

    labels = ["10.0", "2.0", "1.0", "1.10"]
    assert sorted(labels, key=_version_sort_key) == ["1.0", "1.10", "2.0", "10.0"]
    assert _version_sort_key("weird") == (0,)  # non-numeric last-resort


class _VersionSource(_Source):
    def __init__(self, items: list[MigrationItem], history) -> None:
        super().__init__(items)
        self._history = history
        self.version_reads: list[str] = []

    def read_version_history(self, item):
        self.version_reads.append(item.dest_path)
        return self._history


class _VersionTarget(_Target):
    supports_versions = True

    def __init__(self) -> None:
        super().__init__()
        self.labels: list = []
        self.versions: list = []

    def write(self, item, payload):
        self.labels.append(item.version_label)
        self.versions.append(item.versions)
        super().write(item, payload)


def test_runner_loads_and_carries_versions_for_a_version_preserving_target():
    from office365.migration.checkpoint import Checkpoint
    from office365.migration.runner import MigrationRunner

    item = MigrationItem("s", "a")
    history = ("3.0", [("1.0", b"v1"), ("2.0", b"v2")])
    source, target = _VersionSource([item], history), _VersionTarget()

    MigrationRunner().run(
        source,
        target,
        source.list_items(),
        MigrationOptions(),
        Checkpoint.create(),
    )

    assert target.written == ["a"]
    assert target.labels == ["3.0"]
    assert target.versions == [[("1.0", b"v1"), ("2.0", b"v2")]]


def test_runner_does_not_read_versions_for_a_client_side_target():
    from office365.migration.checkpoint import Checkpoint
    from office365.migration.runner import MigrationRunner

    source, target = _VersionSource([MigrationItem("s", "a")], ("1.0", [])), _Target()

    MigrationRunner().run(source, target, source.list_items(), MigrationOptions(), Checkpoint.create())

    assert source.version_reads == []  # client-side target: version history stays untouched


def test_preserve_versions_supported_when_target_and_source_support_it():
    source, target = _VersionSource([], ("1.0", [])), _VersionTarget()
    _assert_fidelity_supported(MigrationOptions(preserve_versions=True), source, target)


def test_preserve_versions_needs_the_source_history_hook():
    source, target = _Source([]), _VersionTarget()  # target can preserve, source cannot supply
    with pytest.raises(NotImplementedError, match="read_version_history"):
        _assert_fidelity_supported(MigrationOptions(preserve_versions=True), source, target)


def test_describe_fidelity_reports_versions_for_a_package_target():
    from office365.migration.fidelity import describe_fidelity

    report = describe_fidelity(
        _VersionSource([], ("1.0", [])), _VersionTarget(), MigrationOptions(preserve_versions=True)
    )
    assert report.ok
    assert "versions" in report.preserved

    client_report = describe_fidelity(
        _VersionSource([], ("1.0", [])), _Target(), MigrationOptions(preserve_versions=True)
    )
    assert not client_report.ok
    assert "versions" in client_report.unsupported


def test_fidelity_matrix_reports_every_dimension_conservatively():
    from office365.migration.fidelity import FidelityStatus, describe_fidelity

    report = describe_fidelity(_Source([]), _Target(), MigrationOptions())
    dims = report.dimensions

    # The full doc-09 §4 dimension set is always reported — no silent gaps.
    assert set(dims) == {
        "content",
        "versions",
        "timestamps",
        "authorship",
        "permissions",
        "attachments",
        "structure",
        "content_types",
        "typed_values",
        "item_state",
        "views",
        "navigation",
        "sharing_links",
    }
    assert dims["content"] == FidelityStatus.DELIVERED.value
    assert dims["navigation"] == FidelityStatus.BEST_EFFORT.value
    assert dims["versions"] == FidelityStatus.UNSUPPORTED.value
    # every non-delivered dimension carries a reason
    for name, status in dims.items():
        if status != FidelityStatus.DELIVERED.value:
            assert name in report.dimension_notes
    assert "content" not in report.dimension_notes


def test_fidelity_matrix_reflects_probed_capabilities():
    from office365.migration.fidelity import FidelityStatus, describe_fidelity

    report = describe_fidelity(
        _FidelitySource([]), _FidelityTarget(), MigrationOptions(preserve_timestamps=True, preserve_permissions=True)
    )

    assert report.dimensions["timestamps"] == FidelityStatus.DELIVERED.value
    assert report.dimensions["permissions"] == FidelityStatus.BEST_EFFORT.value
    assert report.ok


def test_fidelity_matrix_marks_typed_values_best_effort_when_remapping_is_supported():
    from office365.migration.fidelity import FidelityStatus, describe_fidelity

    source, target = _Source([]), _Target()
    source.supports_typed_values = True  # type: ignore[attr-defined]
    target.supports_typed_values = True  # type: ignore[attr-defined]

    report = describe_fidelity(source, target, MigrationOptions())

    assert report.dimensions["typed_values"] == FidelityStatus.BEST_EFFORT.value
    assert "typed_values" in report.dimension_notes


def test_fidelity_matrix_marks_authorship_best_effort_for_a_package_target():
    from office365.migration.fidelity import FidelityStatus, describe_fidelity

    source, target = _VersionSource([], ("1.0", [])), _VersionTarget()
    target.supports_authorship = True  # type: ignore[attr-defined]

    report = describe_fidelity(source, target, MigrationOptions())

    assert report.dimensions["versions"] == FidelityStatus.BEST_EFFORT.value
    assert report.dimensions["authorship"] == FidelityStatus.BEST_EFFORT.value
    assert "authorship" in report.dimension_notes


def test_fidelity_matrix_serializes_and_summarizes():
    import json

    from office365.migration.fidelity import describe_fidelity

    report = describe_fidelity(_Source([]), _Target(), MigrationOptions())

    data = report.to_dict()
    json.dumps(data)  # must be JSON-safe
    assert data["dimensions"] == report.dimensions
    assert "content=delivered" in report.matrix_summary()


def test_sharepoint_adapters_advertise_capabilities():
    from office365.migration.sharepoint.adapters import SharePointListSource, SharePointListTarget
    from office365.migration.sharepoint.package_target import SharePointPackageTarget

    assert SharePointListSource.supports_attachments is True
    assert SharePointListTarget.supports_attachments is True
    assert SharePointListSource.supports_typed_values is True
    assert SharePointListTarget.supports_typed_values is True
    assert SharePointPackageTarget.supports_versions is True
    assert SharePointPackageTarget.supports_authorship is True


def test_library_system_paths_are_excluded():
    from office365.migration.sharepoint.adapters import _is_system_path

    # SharePoint-owned scaffolding is skipped (collides server-side / clobbers pages)
    assert _is_system_path("Forms")
    assert _is_system_path("Forms/AllItems.aspx")
    assert _is_system_path("Forms/Document/")
    assert _is_system_path("desktop.ini")
    # user content is kept
    assert not _is_system_path("doc.txt")
    assert not _is_system_path("Reports/Q1.xlsx")
    assert not _is_system_path("Formsite/notes.txt")  # prefix, not a path segment


def test_item_to_dict_is_json_safe_with_version_blobs():
    import json

    item = MigrationItem("s", "d", version_label="2.0", versions=[("1.0", b"v1")])

    data = item_to_dict(item)

    assert "versions" not in data  # transient blobs are never persisted
    assert data["version_label"] == "2.0"
    json.dumps(data)  # must not raise on bytes
