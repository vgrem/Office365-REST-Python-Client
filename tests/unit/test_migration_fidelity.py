"""Tests for migration metadata capture and honest fidelity guards."""

from __future__ import annotations

import datetime

from office365.migration.adapters.filesystem import FileSystemSource
from office365.migration.base import (
    MigrationItem,
    MigrationOptions,
    PermissionEntry,
    Principal,
    item_from_dict,
    item_to_dict,
)


def test_migration_item_metadata_round_trips():
    item = MigrationItem(
        "src",
        "dst",
        created="2020-01-01T00:00:00",
        modified="2021-01-01T00:00:00",
        author=Principal("i:0#.f|membership|a@contoso.com", "1003200065102863", "Alice", user_id=1),
        editor=Principal("i:0#.f|membership|b@contoso.com", "1003200065102864", "Bob", user_id=2),
    )

    restored = item_from_dict(item_to_dict(item))

    assert restored.created == "2020-01-01T00:00:00"
    assert restored.modified == "2021-01-01T00:00:00"
    assert restored.author is not None and restored.author.user_id == 1
    assert restored.editor is not None and restored.editor.user_id == 2  # noqa: PLR2004


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
        "site_settings",
        "sharing_links",
    }
    assert dims["content"] == FidelityStatus.DELIVERED.value
    assert dims["navigation"] == FidelityStatus.BEST_EFFORT.value
    assert dims["site_settings"] == FidelityStatus.BEST_EFFORT.value
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


# -- a product may declare its own dimensions ------------------------------------
#
# The matrix began as a probe of the SharePoint adapters, so its dimension names are
# SharePoint's (views, navigation, site settings …). A mailbox has none of those, and
# the first Outlook forecast said `attachments: unsupported — list-item attachments are
# carried only between list adapters`, which is true of a list and meaningless for mail.


class _Folder:
    """Just enough of a Graph mail folder for an adapter's label."""

    id = "inbox"
    display_name = "Inbox"


def test_the_mail_import_pair_says_timestamps_cannot_be_restored(tmp_path):
    from office365.migration.fidelity import describe_fidelity
    from office365.migration.outlook import EmlTreeSource, MailboxTarget, MailImportOptions

    report = describe_fidelity(
        EmlTreeSource(tmp_path), MailboxTarget(_Folder(), MailImportOptions()), MigrationOptions()
    )

    # Measured on a live import: Exchange stamps the message with the import time and
    # `receivedDateTime` is not settable, so this is a declared loss, not a mystery.
    assert report.dimensions["timestamps"] == "unsupported"
    assert "receivedDateTime" in report.dimension_notes["timestamps"]
    assert report.dimensions["attachments"] == "delivered"


def test_the_calendar_pairs_name_the_attendee_trade_off(tmp_path):
    from office365.migration.fidelity import describe_fidelity
    from office365.migration.outlook import (
        CalendarExportOptions,
        CalendarImportOptions,
        CalendarSource,
        CalendarTarget,
        IcsExportTarget,
        IcsTreeSource,
    )

    exported = describe_fidelity(
        CalendarSource(_Folder(), CalendarExportOptions()), IcsExportTarget(tmp_path), MigrationOptions()
    )
    imported = describe_fidelity(
        IcsTreeSource(tmp_path), CalendarTarget(_Folder(), CalendarImportOptions()), MigrationOptions()
    )

    assert exported.dimensions["structure"] == "best-effort"
    assert "series master" in exported.dimension_notes["structure"]
    assert imported.dimensions["attendees"] == "best-effort"
    assert "restore_attendees" in imported.dimension_notes["attendees"]
    assert "restore_attendees" not in exported.dimension_notes.get("attendees", "")


def test_the_contact_pairs_declare_what_a_vcard_cannot_carry(tmp_path):
    from office365.migration.fidelity import describe_fidelity
    from office365.migration.outlook import (
        ContactExportOptions,
        ContactImportOptions,
        ContactSource,
        ContactTarget,
        VcfExportTarget,
        VcfTreeSource,
    )

    exported = describe_fidelity(
        ContactSource(_Folder(), ContactExportOptions()), VcfExportTarget(tmp_path), MigrationOptions()
    )
    imported = describe_fidelity(
        VcfTreeSource(tmp_path), ContactTarget(_Folder(), ContactImportOptions()), MigrationOptions()
    )

    assert list(exported.dimensions) == [
        "content",
        "structure",
        "timestamps",
        "item_state",
        "attachments",
        "permissions",
        "versions",
    ]
    assert exported.dimensions["timestamps"] == "delivered"
    assert exported.dimensions["attachments"] == "unsupported"
    assert "photo" in exported.dimension_notes["attachments"]
    # Exchange stamps a contact with the import time, so a re-run cannot restore the
    # contact's own created/modified — a declared loss, not an oversight.
    assert imported.dimensions["timestamps"] == "unsupported"
    assert "import time" in imported.dimension_notes["timestamps"]


def test_the_forecast_report_carries_the_declared_matrix(tmp_path):
    import csv
    import io

    from office365.migration.job import MigrationJob
    from office365.migration.outlook import MailExportTarget, MailFolderSource
    from office365.migration.report import export_reports

    job = MigrationJob(MailFolderSource(_Folder()), MailExportTarget(tmp_path))
    job.fidelity()

    written = export_reports(job, tmp_path / "reports")
    fidelity_csv = tmp_path / "reports" / "FidelityReport.csv"
    rows = list(csv.DictReader(io.StringIO(fidelity_csv.read_text(encoding="utf-8"))))

    assert any(path.endswith("FidelityReport.csv") for path in written)
    assert "views" not in {row["dimension"] for row in rows}
    assert {row["dimension"] for row in rows} == set(job.fidelity().dimensions)
