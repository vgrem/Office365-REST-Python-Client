# Migration

Assess, migrate, monitor, and report using the migration toolkit — a resumable,
checkpointed migration layer built on the client and the data pipeline. Works
**into** SharePoint, **from** it, and between the filesystem / records —
directional (export/import).

The examples mirror the [SharePoint Migration Tool (SPMT) workflow](https://learn.microsoft.com/en-us/sharepointmigration/introducing-the-sharepoint-migration-tool):

**Step 2 — Scan and assess → Step 3 — Create a migration task → Step 4 — Monitor and report**

```
migration/
  assess/          # Step 2 — scan and assess (+ reports/ for the SMAT scan reports)
  migrate/         # Step 3 — create and run a migration task
  monitor/         # Step 4 — monitor and report
```

---

## Prerequisites

| Requirement | Description | Reference |
|---|---|---|
| **Read access** to the target site | Required to scan lists, files, and permissions. | [SharePoint admin roles](https://learn.microsoft.com/en-us/sharepoint/sharepoint-admin-role) |
| **SharePoint admin** (for tenant-scope scans) | [`assess/reports/large_sites.py`](./assess/reports/large_sites.py) enumerates site collections via the SPO.Tenant API — SMAT's farm-account prerequisite. | [SharePoint admin roles](https://learn.microsoft.com/en-us/sharepoint/sharepoint-admin-role) |

---

## Step 2 — Scan and assess

| Operation | File | Required role |
|---|---|---|
| Assess a site (site + subsites) for migration readiness | [`assess/assess_site.py`](./assess/assess_site.py) | Read access |
| Bulk-assess a list of sites | [`assess/assess_bulk.py`](./assess/assess_bulk.py) | Read access |
| Capture a list's structure (columns/content types/views) as JSON | [`assess/capture_structure.py`](./assess/capture_structure.py) | Read access |

```python
from office365.migration import MigrationAssessor
from office365.migration.sharepoint.scanners import LargeSitesScanner
from office365.sharepoint.client_context import ClientContext

ctx = ClientContext("https://contoso.sharepoint.com/sites/team").with_client_certificate(
    "contoso.onmicrosoft.com", client_id="client_id", thumbprint="thumbprint", cert_path="./cert.pem"
)
report = MigrationAssessor(ctx.web).include_permissions().assess(recursive=True).execute_query().value
print(report.summary())  # Webs/Lists/Files/Size + blockers/warnings + ready
print(report.to_records())  # issues as records (CSV/JSON export)
print(report.scan_report(LargeSitesScanner).records)  # typed SMAT-style scan detail
```

### Scan reports (SMAT roadmap)

The assessment is modular — scans are registered in
`office365.migration.sharepoint.registry` (a ScanDef.json analog: name,
scanner, `ReportCategoryType`, `Enabled`). Each scan emits an SMAT-style detail
report (`ScannerReports/<Scan>-detail.csv` + `.json`) and can flag issues on the
assessment report.

```python
from office365.migration.sharepoint.registry import SHAREPOINT_SCANS
from office365.migration.assessment.export import export_assessment

print([d.name for d in SHAREPOINT_SCANS])  # the registered scans
written = export_assessment(report, "out")  # issues + ScannerReports/
```

**Large Sites** (SPSite, on by default) validates site size against the 500 GB
guidance and reports the SMAT columns (SiteId, SiteURL, SiteOwner,
SiteSizeInMB, NumOfWebs, LastContentModifiedDate, TotalItemCount, Hits,
SizeInGB, ...). On-prem-only fields (`ContentDB*`, usage-logging metrics)
report `n/a`. Disable it or any scan with `--disable-scan LargeSites` /
`assessor.disable_scan("LargeSites")` — the assessor then skips collecting its
data.

Generate the tenant-wide `LargeSites-detail.json` report
([`assess/reports/large_sites.py`](./assess/reports/large_sites.py)):

```python
from office365.migration import MigrationTenantAssessor
from office365.migration.sharepoint.scanners import LargeSitesScanner
from office365.sharepoint.tenant.administration.tenant import Tenant

report = MigrationTenantAssessor(Tenant(admin_client)).assess().execute_query().value
scan = report.scan_report(LargeSitesScanner)
print(scan.to_csv())  # SMAT LargeSites-detail.csv (typed rows -> trivial export)
```

Each scan report has a typed row model — the dataclass fields are the SMAT
column headers — so `to_records()` / `to_json()` / `to_csv()` are one-liners
and `None` renders as `n/a`.

Implemented | SMAT roadmap scans (planned)
--- | ---
Large Sites, Locked Sites, File Versions, Large Excel Files, Checked-out files, Browser file handling | Large Lists, Large List Views, Long OneDrive URLs, Unsupported Site Templates, Workflow Associations (2010/2013), ... (see the [SMAT scan reports roadmap](https://learn.microsoft.com/en-us/sharepointmigration/sharepoint-migration-assessment-toolscan-reports-roadmap))

---

## Step 3 — Create a migration task

| Operation | File | Required role |
|---|---|---|
| Copy a local directory tree (filesystem → filesystem) | [`migrate/migrate_files.py`](./migrate/migrate_files.py) | none (local) |
| Export a SharePoint list to local JSON records | [`migrate/export_list.py`](./migrate/export_list.py) | Read access |
| Export/import a document library ↔ local files (`--import`, `--concurrency`) | [`migrate/migrate_library.py`](./migrate/migrate_library.py) | Read/Write access |
| Migrate local files into a library via a migration session (parallel) | [`migrate/migrate_session.py`](./migrate/migrate_session.py) | Write access |
| Migrate a local tree into a library **server-side** (Migration API package; version-history capable) | [`migrate/migrate_library_serverside.py`](./migrate/migrate_library_serverside.py) | Write access (app-only) |
| Build a Migration API package **offline** (inspect the manifest; no tenant) | [`migrate/package_library.py`](./migrate/package_library.py) | none (local) |
| Run an **SPMT-style session** (register → add task → start → show → unregister) | [`migrate/migrate_spmt.py`](./migrate/migrate_spmt.py) | Write access |
| Migrate a **whole site** (every list/library, same tenant) — one resumable job per list | [`migrate/migrate_site.py`](./migrate/migrate_site.py) | Read source + Write target |

```python
from office365.migration import MigrationJob
from office365.migration.adapters.filesystem import FileSystemSource, FileSystemTarget

job = MigrationJob(
    FileSystemSource("src"),
    FileSystemTarget("dst"),
    checkpoint_path="checkpoint.json",  # enables pause/resume
)
job.plan()
job.run()
print(job.stats.summary())
```

### Incremental re-runs

Set `incremental=True` (with `OVERWRITE` conflict resolution) to copy only items
whose source is newer than the target:

```python
from office365.migration import MigrationJob, MigrationOptions, ConflictResolution

job = MigrationJob(
    FileSystemSource("src"),
    FileSystemTarget("dst"),
    options=MigrationOptions(incremental=True, conflict_resolution=ConflictResolution.OVERWRITE),
)
```

### Parallel migration & sessions (fast)

File bytes **cannot ride an OData batch** — SharePoint doesn't support batched file
uploads — so throughput comes from **concurrency**: `MigrationOptions.concurrency`
spins up parallel workers, each on a cloned `ClientContext` (reusing auth +
transport), all sharing one `RateLimiter` that paces the fleet on
`Retry-After` / `X-SharePointHealthScore`. The library target applies this via
its `write_many` fast path over the *deferred* `upload_file`/`upload_content`
primitives. Record/list writes use the JSON-only
`execute_batch(items_per_batch=…, concurrency=…)` instead.

```python
from office365.migration import MigrationJob, MigrationOptions
from office365.migration.adapters.filesystem import FileSystemSource
from office365.migration.sharepoint.adapters import SharePointLibraryTarget

job = MigrationJob(
    FileSystemSource("src"),
    SharePointLibraryTarget(library_folder, concurrency=4),
    options=MigrationOptions(concurrency=4),
)
job.plan()
job.run()
```

A `MigrationSession` coordinates a **batch of migrations** — each task is a
source → target `MigrationJob` added explicitly, then started together:

```python
from office365.migration import MigrationOptions, MigrationSession

session = MigrationSession()
session.add_task(
    FileSystemSource("src-a"),
    SharePointLibraryTarget(library_a, concurrency=4),
    options=MigrationOptions(concurrency=4),
)
session.add_task(
    FileSystemSource("src-b"),
    SharePointLibraryTarget(library_b, concurrency=4),
    options=MigrationOptions(concurrency=4),
)
session.start()
print(session.status())
```

A single migration needs no session — `MigrationJob(source, target, options)`
with `plan()`/`run()`/`verify()` is the primary entry point.

### Server-side migration

The adapters above copy bytes over REST. To carry **version history**, the content
is packaged and ingested by SharePoint **server-side** (the Migration API).
`MigrationJob` now reads a SharePoint library source's version history and carries
it into the package automatically, so a `SharePointLibrarySource` → package job
preserves versions; a local-folder source has none to carry. Authorship and — with
`preserve_permissions=True` — same-tenant ACLs for resolved users are applied
too (requested groups/unresolved principals are skipped with a warning). Azure
Blob Storage is only the courier, and the containers are **SharePoint-owned** — no
Azure account is required.

```
local folder ──▶ package (manifest XML + blobs) ──▶ Azure containers ──▶ library
```

Two examples, two different jobs — you normally run **only the first**:

| Example | What it does | Needs a tenant? |
|---|---|---|
| [`migrate/migrate_library_serverside.py`](./migrate/migrate_library_serverside.py) | the **real migration** (all five steps below) | yes |
| [`migrate/package_library.py`](./migrate/package_library.py) | **optional**: builds the same package **offline** so you can inspect the manifest XML — **not** a prerequisite | no |

#### The real migration — five steps

```python
from office365.migration import MigrationJob
from office365.migration.adapters.filesystem import FileSystemSource
from office365.migration.sharepoint.package_target import SharePointPackageTarget

# 1. Authenticate (app-only)
ctx = ClientContext(site_url).with_client_certificate(tenant, client_id, cert_thumbprint, cert_path)

# 2. Resolve the target web
web = ctx.web.get().execute_query()

# 3. Provision SharePoint-owned containers (SAS URIs + encryption key)
containers = ctx.site.provision_migration_containers().execute_query().value

# 4. Package + submit: files -> manifest XML -> staged blobs -> ingestion job
target = SharePointPackageTarget(
    ctx.site,
    web.id,
    content_uri=containers.DataContainerUri,
    manifest_uri=containers.MetadataContainerUri,
    encryption_key=containers.EncryptionKey,
    list_url="/Documents",
)
job = MigrationJob(FileSystemSource("../../../data"), target)  # examples/data
job.plan()
job.run()  # stages the package and submits the job
print(target.job_id)

# 5. Monitor until terminal (GetMigrationJobProgress)
target.monitor()
```

```bash
cd examples/sharepoint/migration/migrate
python migrate_library_serverside.py                  # defaults to examples/data
```

#### See the package first (optional, no tenant)

```bash
cd examples/sharepoint/migration/migrate
python package_library.py                             # writes $TMPDIR/spo-package/
# open $TMPDIR/spo-package/manifest/Manifest.xml
```

The migration above builds this package internally — `package_library.py` just
lets you look at the payload (manifest XML + content blobs) without SharePoint or
Azure. It is a learning/debugging aid, not a step you must run first.

---

## Step 4 — Monitor and report

| Operation | File | Required role |
|---|---|---|
| Migrate a tree and write one JSON migration report | [`monitor/export_reports.py`](./monitor/export_reports.py) | none (local) |
| Verify a target list's structure against the source (read-only) | [`monitor/verify_structure.py`](./monitor/verify_structure.py) | Read access (both sites) |
| Monitor a local migration (live progress, Ctrl-C pause, re-run to resume) | [`monitor/monitor.py`](./monitor/monitor.py) | none (local) |
| Monitor server-side ingestion jobs concurrently (async) | [`monitor/monitor_async.py`](./monitor/monitor_async.py) | SharePoint admin |

```python
job.export_reports("reports")  # SummaryReport / ItemReport / FailureReport (CSV + JSON)
print(job.verify().summary())  # reconcile source vs target
```

Reports carry SPMT-style summary columns (total/migrated/not-migrated bytes & GB,
items, GB/hour, run id, timestamps) plus per-item `file_name`, `extension`,
`error`, and `error_code`; the failure report is only written when failures
occur.

`job.verify()` never looks at the *container*, so pair it with a structure check
that compares the source and target lists' columns, content types, and views:

```python
from office365.migration.sharepoint import verify_list_structure

report = verify_list_structure(source_list, target_list)
print(report.summary())  # "MISMATCH | Projects | columns: 2, content types: 1, views: 0, field links: 1"
```

```bash
cd examples/sharepoint/migration/monitor
python verify_structure.py --list Projects --target-site https://contoso.sharepoint.com/sites/projects-copy
```

For **record lists**, `job.verify()` pairs source and target items through the
`MigrationSourceId` marker the target adds to every migrated list (attachments are
presence- and md5-checked; record content stays `unverifiable`). The same marker
makes the default `SKIP` policy idempotent, so re-running skips items already on
the target instead of duplicating them.

To watch a migration live — progress bars for planning/migrating, and a clean
SPMT-style pause on **Ctrl-C** (the checkpoint is saved; re-running the same
command resumes) — use the monitor example (any local directories, no
credentials needed):

```bash
python monitor/monitor.py --source ./data-a --target ./dst-a
```

For a **server-side ingestion job** submitted through the SharePoint Migration
API, `monitor/monitor_async.py` polls `GetMigrationJobProgress` with the
awaitable `MigrationServerJob.monitor_async()` — watching one or more job ids at
once and surfacing any `JobError` events:

```bash
python monitor/monitor_async.py --job-id <job-id> --job-id <job-id>
```

---

## API reference

- [SharePoint Migration API](https://learn.microsoft.com/en-us/sharepoint/dev/apis/migration-api-reference)
- [SMAT scan reports roadmap](https://learn.microsoft.com/en-us/sharepointmigration/sharepoint-migration-assessment-toolscan-reports-roadmap)
- [Large Sites scan](https://learn.microsoft.com/en-us/sharepointmigration/migration-assessment-scan-large-sites)
- [Locked Sites scan](https://learn.microsoft.com/en-us/sharepointmigration/migration-assessment-scan-locked-sites)
