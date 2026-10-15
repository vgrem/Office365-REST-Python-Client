"""Pre-migration assessment — core resilience, typed reports, registry and adapters.

Kept deliberately compact: one test per important behavior (walkers skip what
they cannot read, report rows are typed, the registry gates scans, and the
SharePoint/Outlook adapters degrade gracefully).
"""

from __future__ import annotations

from datetime import datetime
from types import SimpleNamespace
from typing import TYPE_CHECKING, cast

if TYPE_CHECKING:
    from office365.sharepoint.lists.list import List as SPList

from office365.migration import (
    MailboxAssessor,
    MigrationAssessor,
    MigrationTenantAssessor,
    OutlookOptions,
)
from office365.migration.assessment.containers import ScanContainer
from office365.migration.assessment.issue import AssessmentIssue
from office365.migration.assessment.report import AssessmentReport
from office365.migration.assessment.scanners import ScanTarget
from office365.migration.sharepoint import SharePointAssessmentOptions
from office365.migration.sharepoint.adapters import SharePointListSource
from office365.migration.sharepoint.registry import sharepoint_scan_pairs
from office365.migration.sharepoint.scanners import FieldScanner, LargeSitesScanner
from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.tenant.administration.tenant import Tenant
from tests._scripted_transport import ScriptedTransport

_GB = 1024**3
_ISOLATED = SharePointAssessmentOptions(
    disabled_scans={
        "permissions",
        "fields",
        "lookups",
        "largeLists",
        "paths",
        "files",
        "FileVersions",
        "CheckedOutFiles",
        "LargeExcelFiles",
        "LongOneDriveUrls",
        "BrowserFileHandling",
        "ThicketFolder",
        "UnsupportedSiteTemplates",
    }
)


# ── Web-scope payloads / helpers ─────────────────────────────────────────────


def _site() -> dict:
    return {
        "__metadata": {"type": "SP.Site"},
        "Id": "11111111-1111-1111-1111-111111111111",
        "Url": "https://contoso.sharepoint.com/sites/big",
        "Owner": {"__metadata": {"type": "SP.User"}, "Title": "Site Owner", "Email": "owner@contoso.com"},
    }


def _list(list_id: str, title: str, item_count: int = 0, modified: str = "2024-01-02T03:04:05Z") -> dict:
    return {
        "__metadata": {"type": "SP.List"},
        "Id": list_id,
        "Title": title,
        "Hidden": False,
        "ItemCount": item_count,
        "LastItemModifiedDate": modified,
    }


def _file() -> dict:
    return {
        "__metadata": {"type": "SP.ListItem"},
        "FileRef": "/sites/x/Shared Documents/a.txt",
        "FileLeafRef": "a.txt",
        "File": {"__metadata": {"type": "SP.File"}, "Length": 100},
    }


def _web(url: str) -> dict:
    return {"__metadata": {"type": "SP.Web"}, "Url": url}


def _run_web(payloads: list, options: SharePointAssessmentOptions | None = None) -> AssessmentReport:
    ctx = ClientContext("https://contoso.sharepoint.com/sites/x")
    ctx.pending_request().beforeExecute.clear()
    ctx.pending_request().transport = ScriptedTransport(payloads)
    return MigrationAssessor(ctx.web, options or SharePointAssessmentOptions()).assess().execute_query().value


def test_inaccessible_list_is_skipped_not_fatal():
    report = _run_web(
        [
            _site(),  # site collection metadata (LargeSites)
            {"d": {"results": [_list("1", "Restricted"), _list("2", "Public")]}},  # web.lists
            {"d": {"results": []}},  # web.webs
            {"d": {"results": []}},  # Restricted.fields
            ("deny",),  # Restricted.items -> 403
            {"d": {"results": []}},  # Public.fields
            {"d": {"results": [_file()]}},  # Public.items
        ]
    )
    assert report.total_lists == 2  # noqa: PLR2004
    assert report.total_files == 1  # only the accessible list was scanned
    access = [i for i in report.issues if i.category == "access"]
    assert len(access) == 1 and "lists/Restricted" in access[0].location


def test_recursive_scan_aggregates_webs_lists_and_files():
    report = _run_web(
        [
            _site(),
            {"d": {"results": [_list("1", "RootList")]}},  # root.lists
            {"d": {"Webs": {"results": [_web("https://x/sites/sub1")]}}},  # get_all_webs
            {"d": {"results": []}},  # RootList.fields
            {"d": {"results": [_file()]}},  # RootList.items
            {"d": {"Webs": {"results": []}}},  # sub1.webs
            {"d": {"results": [_list("2", "SubList")]}},  # sub1.lists
            {
                "d": {
                    "results": [
                        {
                            "__metadata": {"type": "SP.Field"},
                            "InternalName": "MyField",
                            "SchemaXml": '<Field ReadOnly="TRUE" SourceID="x"/>',
                        }
                    ]
                }
            },  # SubList.fields
            {"d": {"results": [_file()]}},  # SubList.items
        ]
    )
    assert (report.total_webs, report.total_lists, report.total_files) == (1, 2, 2)
    assert any(i.location.startswith("https://x/sites/sub1/lists/") for i in report.issues)


def test_large_site_record_is_typed_and_flagged():
    report = _run_web(
        [
            {**_site(), "UsageInfo": {"Storage": 600 * _GB, "Hits": 1000}},
            {"d": {"results": [_list("1", "Docs", 1000), _list("2", "Assets", 2000)]}},
            {"d": {"Webs": {"results": [_web("https://x/sub1")]}}},
            {"d": {"Webs": {"results": []}}},
            {"d": {"results": []}},
        ],
        options=_ISOLATED,
    )

    scan = report.scan_report(LargeSitesScanner)
    assert len(scan.records) == 1
    row = scan.records[0]
    assert row.SiteId == "11111111-1111-1111-1111-111111111111"
    assert row.SiteURL == "https://contoso.sharepoint.com/sites/big"
    assert row.SiteOwner == "Site Owner"
    assert row.SizeInGB == 600.0  # noqa: PLR2004
    assert row.NumOfWebs == 1
    assert row.TotalItemCount == 3000  # noqa: PLR2004
    assert row.Hits == 1000  # noqa: PLR2004
    assert row.ScanID == report.scan_id
    assert scan.to_records()[0]["ContentDBName"] == "n/a"  # on-prem-only column

    warnings = [i for i in report.issues if i.category == "site" and i.severity == "warning"]
    assert len(warnings) == 1 and "600.0GB" in warnings[0].message


# ── Tenant scope ─────────────────────────────────────────────────────────────


def _site_props(site_id: str, url: str, storage_gb: int, webs: int = 3) -> dict:
    return {
        "__metadata": {"type": "Microsoft.Online.SharePoint.TenantAdministration.SiteProperties"},
        "SiteId": site_id,
        "Url": url,
        "StorageUsage": storage_gb * _GB,
        "WebsCount": webs,
        "OwnerLoginName": "owner@contoso.com",
        "LastContentModifiedDate": "2024-01-02T03:04:05Z",
        "LockState": "Unlock",
    }


def _run_tenant(payloads: list) -> AssessmentReport:
    ctx = ClientContext("https://contoso-admin.sharepoint.com")
    ctx.pending_request().beforeExecute.clear()
    ctx.pending_request().transport = ScriptedTransport(payloads)
    return MigrationTenantAssessor(Tenant(ctx)).assess().execute_query().value


def test_tenant_large_sites_filters_sorts_and_skips_locked():
    locked = _site_props("9", "https://x/locked", 900)
    locked["LockState"] = "Locked"
    report = _run_tenant(
        [
            {
                "d": {
                    "results": [
                        _site_props("1", "https://x/huge", 700, webs=12),
                        _site_props("2", "https://x/bigger", 900),
                        _site_props("3", "https://x/small", 50),
                        _site_props("4", "https://x/exactly", 500),
                        locked,
                    ]
                }
            }
        ]
    )

    rows = report.scan_report(LargeSitesScanner).records
    assert [r.SizeInGB for r in rows] == [900.0, 700.0]  # locked + <=500GB excluded, sorted desc
    assert rows[1].SiteURL == "https://x/huge" and rows[1].NumOfWebs == 12  # noqa: PLR2004
    assert rows[0].ScanID == report.scan_id


# ── Scanner + registry ───────────────────────────────────────────────────────


def test_field_scanner_ignores_system_fields_flags_user_fields():
    report = AssessmentReport()
    fields = [
        {"InternalName": "ID", "SchemaXml": '<Field Type="Counter" ReadOnly="TRUE" SourceID="x"/>'},
        {"InternalName": "MyField", "SchemaXml": '<Field Type="Text" ReadOnly="TRUE" SourceID="x" ColName="x"/>'},
    ]
    FieldScanner(SharePointAssessmentOptions()).run(
        ScanTarget(ScanContainer.FIELDS, [SimpleNamespace(properties=f) for f in fields], "lists/L"),
        report,
    )
    assert not any(i.location.endswith("/ID") for i in report.issues)
    assert any(i.severity == "warning" and i.location.endswith("/MyField") for i in report.issues)
    assert any(i.severity == "info" and i.location.endswith("/MyField") for i in report.issues)


def test_registry_gates_scans_and_disabling_drops_site_query():
    names = {d.name for d, _ in sharepoint_scan_pairs(SharePointAssessmentOptions())}
    assert {"fields", "paths", "LargeSites"} <= names and "permissions" not in names

    options = SharePointAssessmentOptions()
    containers = {d.name: d.container for d, _ in sharepoint_scan_pairs(options) if d.name in ("fields", "LargeSites")}
    assert containers["fields"] is ScanContainer.FIELDS
    assert containers["LargeSites"] is ScanContainer.SITE

    ctx = ClientContext("https://contoso.sharepoint.com/sites/x")
    ctx.pending_request().beforeExecute.clear()
    transport = ScriptedTransport([{"d": {"results": []}}, {"d": {"results": []}}])
    ctx.pending_request().transport = transport
    options = SharePointAssessmentOptions(
        disabled_scans={
            "permissions",
            "fields",
            "paths",
            "files",
            "FileVersions",
            "CheckedOutFiles",
            "LargeExcelFiles",
            "LongOneDriveUrls",
            "BrowserFileHandling",
            "ThicketFolder",
            "LargeSites",
            "UnsupportedSiteTemplates",
        }
    )
    report = MigrationAssessor(ctx.web, options).assess().execute_query().value
    assert transport.calls == 2  # noqa: PLR2004 — no site-collection query issued
    assert report.scan_reports == {}


# ── SharePoint list adapter fallbacks ────────────────────────────────────────


class _Item:
    def __init__(self, item_id: int, properties: dict):
        self.id = item_id
        self.properties = properties


class _Field:
    def __init__(self, internal_name: str, type_as_string: str = "", schema_xml: str = "", hidden: bool = False):
        self.internal_name = internal_name
        self.type_as_string = type_as_string
        self.schema_xml = schema_xml
        self.hidden = hidden


class _QueryOptions:
    def __init__(self, select):
        self.select = select or []
        self.expand: list[str] = []


class _LoadedCollection(list):
    """A loaded collection stub exposing the query options the projection reads."""

    def __init__(self, items, select):
        super().__init__(items)
        self.query_options = _QueryOptions(select)


class _Query:
    def __init__(self, load, select):
        self._load = load
        self._select = select

    def execute_query(self):
        return _LoadedCollection(self._load(self._select), self._select)


class _ItemsEndpoint:
    def __init__(self, load):
        self._load = load
        self._select = None

    def select(self, columns: list[str]):
        self._select = columns
        return self

    def expand(self, _expands):
        return self

    def get_all(self):
        return _Query(self._load, self._select)


class _List:
    def __init__(self, load, fields: list[_Field], title: str = "Docs"):
        self.title = title
        self.items = _ItemsEndpoint(load)

        class _FieldsEndpoint:
            def get(self):
                return _Query(lambda _: fields, None)

        self.fields = _FieldsEndpoint()


class _TaxonomyError(Exception):
    """Duck-type of a ClientRequestException from an orphaned term set."""

    def __init__(self):
        super().__init__("The given guid does not exist in the term store")
        self.code = "-2146232832, Microsoft.SharePoint.SPFieldValidationException"
        self.message = "The given guid does not exist in the term store"


def test_list_source_taxonomy_failure_falls_back_to_safe_select():
    selects = []

    def load(select):
        selects.append(select)
        if select is None or "*" in select:
            raise _TaxonomyError()
        return [_Item(1, {k: "" for k in select})]

    fields = [
        _Field("Id"),
        _Field("Title"),
        _Field("Topics", type_as_string="TaxonomyFieldType"),
        _Field("Tags", schema_xml='<Field ... TermSetId="1234-..."/>'),
        _Field("MainLinkSettings", hidden=True),
    ]
    source = SharePointListSource(cast("SPList", _List(load, fields)))
    result = source.list_items()

    assert len(result) == 1
    assert any("excluded Managed Metadata" in w for w in source.warnings)
    assert "Topics" not in selects[-1] and "Tags" not in selects[-1]
    assert "MainLinkSettings" not in selects[-1]  # hidden/system columns not projected
    assert "Topics" not in source.read(result[0])


def test_list_source_denied_cascades_to_id_title_only():
    selects = []

    def load(select):
        selects.append(select)
        if select is None or "*" in select:
            raise _TaxonomyError()
        if len(select) > 2:  # noqa: PLR2004 — the visible-column read is denied too
            raise PermissionError("denied")
        return [_Item(1, {"Id": 1, "Title": "only"})]

    fields = [_Field("Id"), _Field("Title"), _Field("Notes")]
    source = SharePointListSource(cast("SPList", _List(load, fields)))
    result = source.list_items()

    assert len(result) == 1
    assert selects[-1] == ["Id", "Title"]
    assert any("denied too" in w for w in source.warnings)


# ── Outlook mailbox walker ───────────────────────────────────────────────────


class _FoldersEndpoint:
    def __init__(self, items):
        self._items = items

    def select(self, _columns):
        return self

    def get(self):
        return self

    def execute_query(self):
        return self._items


class _MailFolder:
    def __init__(self, name, item_count=0, unread_count=0, children=None, folder_id=None):
        self.display_name = name
        self.id = folder_id or name
        self.total_item_count = item_count
        self.unread_item_count = unread_count
        self.child_folder_count = len(children or [])
        self.child_folders = _FoldersEndpoint(children or [])


def _run_mailbox(folders, options: OutlookOptions | None = None) -> AssessmentReport:
    class _User:
        mail_folders = _FoldersEndpoint(folders)

    return MailboxAssessor(_User(), options or OutlookOptions()).assess()


def test_mailbox_walker_reports_nested_counts_and_flags_large_folder():
    report = _run_mailbox(
        [
            _MailFolder(
                "Inbox",
                item_count=12,
                unread_count=3,
                children=[_MailFolder("Projects", item_count=5, unread_count=1, folder_id="p1")],
            ),
            _MailFolder("Archive", item_count=150_000, folder_id="a1"),
        ],
        OutlookOptions(large_folder_items=100_000),
    )

    rows = {row["FolderPath"]: row for row in report.scan_reports["MailFolders"].to_records()}
    assert rows["Inbox"]["ItemCount"] == 12  # noqa: PLR2004
    assert rows["Inbox/Projects"]["ItemCount"] == 5  # noqa: PLR2004
    flags = [i for i in report.issues if i.category == "mail"]
    assert len(flags) == 1 and "Archive" in flags[0].location


# ── Limit-driven scanners (SPMT risk codes) ──────────────────────────────────


def test_large_list_scanner_grades_by_threshold():
    from office365.migration.sharepoint.scanners.large_lists import LargeListScanner

    scanner = LargeListScanner(SharePointAssessmentOptions())
    for count, severity, code in (
        (100, None, ""),
        (6000, "info", "LIST_VIEW_EXCEED_LIMIT"),
        (25_000, "warning", "ITEM_COUNT_EXCEED_INDEX_LIMIT"),
        (30_000_001, "blocker", "ITEM_COUNT_EXCEED_LIMIT"),
    ):
        report = AssessmentReport.new()
        entity = SimpleNamespace(item_count=count, title="L")
        scanner.run(ScanTarget(ScanContainer.LIST, entity, "web/lists/L"), report)
        if severity is None:
            assert not report.issues
        else:
            assert len(report.issues) == 1
            assert report.issues[0].severity == severity
            assert report.issues[0].risk_code == code


def test_file_versions_scanner_reports_versioned_files():
    from office365.migration.sharepoint.scanners.file_versions import FileVersionsScanner

    class _File:
        def __init__(self, major, minor):
            self.major_version = major
            self.minor_version = minor

    items = [
        SimpleNamespace(properties={"FileRef": "/sites/x/Docs/current.txt"}, file=_File(1, 0)),
        SimpleNamespace(properties={"FileRef": "/sites/x/Docs/history.txt"}, file=_File(3, 1)),
    ]
    report = AssessmentReport.new()
    scanner = FileVersionsScanner(SharePointAssessmentOptions())
    scanner.run(ScanTarget(ScanContainer.ITEMS, items, "https://x/sites/x/lists/Docs"), report)

    assert len(scanner.records) == 1
    row = scanner.records[0]
    assert row.File == "/sites/x/Docs/history.txt"
    assert row.VersionCount == 4  # noqa: PLR2004 — 3 major + 1 minor
    assert row.SiteURL == "https://x/sites/x"
    assert row.ScanID == report.scan_id


def test_checked_out_files_scanner_reports_and_warns():
    from office365.migration.sharepoint.scanners.checked_out_files import CheckedOutFilesScanner

    class _File:
        def __init__(self, check_out_type, user=None):
            self.check_out_type = check_out_type
            self.checked_out_by_user = user

    user = SimpleNamespace(login_name="i:0#.f|membership|jane@contoso.com", title="Jane")
    items = [
        SimpleNamespace(properties={"FileRef": "/sites/x/Docs/free.txt"}, file=_File(0)),
        SimpleNamespace(properties={"FileRef": "/sites/x/Docs/locked.txt"}, file=_File(1, user)),
    ]
    report = AssessmentReport.new()
    scanner = CheckedOutFilesScanner(SharePointAssessmentOptions())
    scanner.run(ScanTarget(ScanContainer.ITEMS, items, "https://x/sites/x/lists/Docs"), report)

    assert len(scanner.records) == 1
    row = scanner.records[0]
    assert row.File == "/sites/x/Docs/locked.txt"
    assert row.CheckedOutUser == "i:0#.f|membership|jane@contoso.com"
    assert row.SiteURL == "https://x/sites/x"
    assert row.ScanID == report.scan_id
    assert any(i.severity == "warning" and "checked-out" in i.message for i in report.issues)


def test_large_excel_files_scanner_filters_by_size():
    from office365.migration.sharepoint.scanners.large_excel_files import LargeExcelFilesScanner

    class _File:
        def __init__(self, length):
            self.length = length

    mb = 1024 * 1024
    items = [
        SimpleNamespace(properties={"FileLeafRef": "a.xlsx", "FileRef": "/sites/x/Docs/a.xlsx"}, file=_File(2 * mb)),
        SimpleNamespace(properties={"FileLeafRef": "b.xlsm", "FileRef": "/sites/x/Docs/b.xlsm"}, file=_File(12 * mb)),
        SimpleNamespace(properties={"FileLeafRef": "c.docx", "FileRef": "/sites/x/Docs/c.docx"}, file=_File(20 * mb)),
    ]
    report = AssessmentReport.new()
    scanner = LargeExcelFilesScanner(SharePointAssessmentOptions())
    scanner.run(ScanTarget(ScanContainer.ITEMS, items, "https://x/sites/x/lists/Docs"), report)

    assert len(scanner.records) == 1
    row = scanner.records[0]
    assert row.File == "/sites/x/Docs/b.xlsm"
    assert row.FileSizeinMB == 12.0  # noqa: PLR2004


def test_browser_file_handling_scanner_reports_html():
    from office365.migration.sharepoint.scanners.browser_file_handling import BrowserFileHandlingScanner

    class _File:
        def __init__(self):
            self.time_created = datetime(2020, 1, 1)
            self.time_last_modified = datetime(2021, 1, 1)
            self.modified_by = SimpleNamespace(login_name="i:0#.f|membership|jane@contoso.com", title="Jane")

    items = [
        SimpleNamespace(properties={"FileLeafRef": "page.html", "FileRef": "/sites/x/Docs/page.html"}, file=_File()),
        SimpleNamespace(properties={"FileLeafRef": "doc.docx", "FileRef": "/sites/x/Docs/doc.docx"}, file=_File()),
    ]
    report = AssessmentReport.new()
    scanner = BrowserFileHandlingScanner(SharePointAssessmentOptions())
    scanner.run(ScanTarget(ScanContainer.ITEMS, items, "https://x/sites/x/lists/Docs"), report)

    assert len(scanner.records) == 1
    row = scanner.records[0]
    assert row.File == "/sites/x/Docs/page.html"
    assert row.ModifiedBy == "i:0#.f|membership|jane@contoso.com"
    assert row.TimeCreated == datetime(2020, 1, 1)


def test_thicket_folder_scanner_flags_only_folders():
    from office365.migration.sharepoint.scanners.thicket_folders import ThicketFolderScanner

    class _File:
        pass

    items = [
        SimpleNamespace(properties={"FileRef": "/sites/x/Docs/page_files", "FileLeafRef": "page_files"}, file=None),
        SimpleNamespace(properties={"FileRef": "/sites/x/Docs/notes_file", "FileLeafRef": "notes_file"}, file=None),
        SimpleNamespace(properties={"FileRef": "/sites/x/Docs/a.txt", "FileLeafRef": "a.txt"}, file=_File()),
    ]
    report = AssessmentReport.new()
    ThicketFolderScanner(SharePointAssessmentOptions()).run(
        ScanTarget(ScanContainer.ITEMS, items, "https://x/sites/x/lists/Docs"), report
    )
    assert len(report.issues) == 2  # noqa: PLR2004
    assert {i.risk_code for i in report.issues} == {"THICKET_FOLDER_UNSUPPORTED"}
    assert all(i.severity == "blocker" for i in report.issues)
    assert not any(i.location.endswith("a.txt") for i in report.issues)


def test_long_onedrive_urls_scanner_measures_full_url():
    from office365.migration.sharepoint.scanners.long_onedrive_urls import LongOneDriveUrlsScanner

    long_path = "/sites/x/Docs/" + "a" * 420 + ".txt"
    items = [
        SimpleNamespace(properties={"FileRef": long_path}),
        SimpleNamespace(properties={"FileRef": "/sites/x/Docs/short.txt"}),
    ]
    report = AssessmentReport.new()
    scanner = LongOneDriveUrlsScanner(SharePointAssessmentOptions())
    scanner.run(ScanTarget(ScanContainer.ITEMS, items, "https://contoso.sharepoint.com/sites/x/lists/Docs"), report)

    assert len(scanner.records) == 1
    row = scanner.records[0]
    assert row.File == long_path
    assert row.UrlLength == len("https://contoso.sharepoint.com" + long_path)
    assert row.SiteURL == "https://contoso.sharepoint.com/sites/x"
    assert row.ScanID == report.scan_id


def test_unsupported_site_templates_scanner_reports_legacy_templates():
    from office365.migration.sharepoint.scanners.summary import SiteScanSummary
    from office365.migration.sharepoint.scanners.unsupported_site_templates import UnsupportedSiteTemplatesScanner

    report = AssessmentReport.new()
    scanner = UnsupportedSiteTemplatesScanner(SharePointAssessmentOptions())
    supported = SiteScanSummary(site_url="https://x/sites/a", web_template="STS#0")
    legacy = SiteScanSummary(site_url="https://x/sites/b", web_template="SPSMSITEHOST#0")
    scanner.run(ScanTarget(ScanContainer.SITE, supported, "https://x/sites/a"), report)
    scanner.run(ScanTarget(ScanContainer.SITE, legacy, "https://x/sites/b"), report)

    assert len(scanner.records) == 1
    row = scanner.records[0]
    assert row.URL == "https://x/sites/b"
    assert row.Template == "SPSMSITEHOST#0"
    assert row.ScanID == report.scan_id


def test_lookup_column_scanner_flags_too_many_lookups():
    from office365.migration.sharepoint.scanners.lookup import LookupColumnScanner

    fields = [SimpleNamespace(properties={"InternalName": f"L{i}", "TypeAsString": "Lookup"}) for i in range(9)]
    report = AssessmentReport.new()
    options = SharePointAssessmentOptions()
    LookupColumnScanner(options).run(ScanTarget(ScanContainer.FIELDS, fields, "web/lists/L"), report)
    assert len(report.issues) == 1
    assert report.issues[0].risk_code == "LIST_VIEW_LOOKUP_EXCEED_LIMIT"


def test_permission_scanner_uses_unique_scope_limits():
    from office365.migration.sharepoint.scanners.permissions import PermissionScanner

    items = [SimpleNamespace(properties={"HasUniqueRoleAssignments": True}) for _ in range(6000)]
    report = AssessmentReport.new()
    PermissionScanner(SharePointAssessmentOptions()).run(ScanTarget(ScanContainer.ITEMS, items, "web/lists/L"), report)
    assert len(report.issues) == 1
    assert report.issues[0].severity == "warning"
    assert report.issues[0].risk_code == "UNIQUE_PERMISSION_EXCEED_LIMIT"


def test_report_groups_by_risk_code():
    report = AssessmentReport.new()
    report.issues.append(AssessmentIssue("warning", "list", "x", "m", risk_code="LIST_VIEW_EXCEED_LIMIT"))
    assert report.by_risk_code == {"LIST_VIEW_EXCEED_LIMIT": 1}
    assert report.to_records()[0]["risk_code"] == "LIST_VIEW_EXCEED_LIMIT"


# ── Limits integration ───────────────────────────────────────────────────────


def test_assessment_options_seed_limit_mapping():
    from office365.sharepoint.thresholds import Limits

    options = SharePointAssessmentOptions()
    assert options.limit("list_view_threshold") is Limits.LIST_VIEW
    assert options.limit("max_list_items") is Limits.MAX_LIST_ITEMS
    assert options.limit("unique_scopes") is Limits.UNIQUE_SCOPES


def test_scanner_issue_carries_the_limit():
    from office365.migration.sharepoint.scanners.large_lists import LargeListScanner
    from office365.sharepoint.thresholds import Limits

    report = AssessmentReport.new()
    entity = SimpleNamespace(item_count=6000, title="L")
    LargeListScanner(SharePointAssessmentOptions()).run(ScanTarget(ScanContainer.LIST, entity, "web/lists/L"), report)

    issue = report.issues[0]
    assert issue.limit is Limits.LIST_VIEW
    assert issue.risk_code == "LIST_VIEW_EXCEED_LIMIT"
    assert "list view threshold" in issue.message
