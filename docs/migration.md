# Migration

Move content between Microsoft 365 and other systems — resumable, verifiable,
and with best-effort fidelity. The toolkit is product-agnostic (a `DataSource`
→ `DataTarget` pair) and ships adapters for the filesystem, SharePoint lists,
and SharePoint document libraries.

## The model

| Piece | Role |
|---|---|
| `DataSource` / `DataTarget` | adapters — `read`/`checksum` and `exists`/`write`/`list_paths` |
| `MigrationJob` | lifecycle `assess → plan → run → verify`, resumable |
| `Manifest` | the persisted plan (a list of `MigrationItem`) |
| `Checkpoint` | per-item status, incremental watermarks, phase (pause/resume/cancel) |
| `MigrationServerJob` | server-side Migration API ingestion (submit + monitor) |

## Quick start

Filesystem → SharePoint document library:

```python
from office365.migration import MigrationJob, MigrationOptions
from office365.migration.adapters.filesystem import FileSystemSource
from office365.migration.sharepoint.adapters import SharePointLibraryTarget
from office365.sharepoint.client_context import ClientContext

ctx = ClientContext(site_url).with_client_certificate(tenant, client_id, thumbprint, cert_path)
library = ctx.web.lists.get_by_title("Documents").root_folder

job = MigrationJob(
    FileSystemSource("src"),
    SharePointLibraryTarget(library),
    MigrationOptions(concurrency=4),
)
job.plan()
job.run()
print(job.stats.summary())
print(job.verify().summary())
job.export_reports("reports/")
```

Runs are **idempotent and resumable**: pass `manifest_path` / `checkpoint_path`
and a paused or failed run continues where it stopped (`job.resume()`). Set
`MigrationOptions(incremental=True)` to skip items at or below the persisted
watermark. Checkpoints are persisted **atomically** (temp file → `fsync` →
rename), so a crash mid-save never corrupts the file the next run resumes from.

## Idempotency & conflicts

A re-run must not duplicate content. Two mechanisms cooperate:

- **Per-item checkpoint** — items already `done`/`skipped` aren't re-driven, so a
  resumed run continues where it stopped.
- **Conflict policy** — `MigrationOptions(conflict_resolution=…)` decides what a
  target that already exists should do:
  - `SKIP` (default) — leave it untouched;
  - `OVERWRITE` — replace it;
  - `RENAME` — land beside it under a numeric suffix.

The runner applies the policy to file targets directly. Record targets (such as
`SharePointListTarget` with a `key`) receive it through an optional
`configure(options)` hook: `OVERWRITE` maps to the record pipeline's
`on_conflict="update"` (keyed create-or-reconcile), everything else to
`on_conflict="skip"`. Passing an explicit `on_conflict=` to a record target pins
it regardless of the options. This is the same `on_conflict` vocabulary the data
pipeline uses (see [Data pipeline](data-pipeline.md)).

> **SPMT, accurately.** The SharePoint Migration Tool's exactly-once reliability
> comes from a *server-managed, keyed* bulk import (the Migration API) that
> reconciles identity server-side — **not** from an HTTP `PATCH`/`PUT` upsert
> pattern. The client-side runner therefore can't reproduce SPMT's semantics; the
> server-side path (`MigrationServerJob`) is what does.

## Adapters

| Adapter | Direction | Content |
|---|---|---|
| `FileSystemSource` / `FileSystemTarget` | both | files + folders |
| `JsonFileSource` / `JsonFileTarget` | both | record payloads (one JSON file per item) |
| `SharePointLibrarySource` / `SharePointLibraryTarget` | both | files + folders (recursive) |
| `SharePointListSource` / `SharePointListTarget` | both | list items as records |
| `TeamsArchiveSource` / `TeamsArchiveTarget` | both | Teams archives |

## SPMT-style sessions

`MigrationSession` mirrors the
[SPMT PowerShell cmdlets](https://learn.microsoft.com/en-us/powershell/module/microsoft.sharepoint.migrationtool.powershell/)
— register a session, add tasks, start, show, stop:

| cmdlet | method |
|---|---|
| `Register-SPMTMigration` | `session.register(settings=..., context=...)` |
| `Add-SPMTTask` | `session.add_task(file_share_source=..., target_site_url=..., target_list=...)` |
| `Show-SPMTMigration` | `session.show()` |
| `Start-SPMTMigration` | `session.start()` |
| `Stop-SPMTMigration` | `session.stop()` |
| `Unregister-SPMTMigration` | `session.unregister()` |

```python
from office365.migration import MigrationSession, MigrationSettings

session = MigrationSession().register(
    context=ctx,  # a SharePoint ClientContext
    settings=MigrationSettings(use_migration_api=True),  # server-side Migration API
)
session.add_task(
    file_share_source="C:/src",
    target_site_url="https://contoso.sharepoint.com/sites/team",
    target_list="Documents",
)
session.start()
print(session.show())
session.unregister()
```

`MigrationSettings` mirrors `Register-SPMTMigration` (permissions, timestamps,
versions, filters, user mapping, Azure storage…); the subset the core enforces is
mapped by `to_options()`, which the session applies to every task by default (pass
`options=` to a task, or `MigrationSession(options=...)`, to override). Tasks can
also be declared as `MigrationTask` objects or parsed
from the SPMT JSON task format (`MigrationTask.from_json(...)`). A resolved
SharePoint task replays the source list's columns, content types and views onto
the (existing) target list before content is copied; pass
`provision_structure=False` to `add_task` / `add_site_task` to skip that.

### Whole-site migration

A `MigrationTask(migrate_all=True)` covers **every list and document library** on
the source site. `session.add_site_task(...)` resolves it into **one job per
list** — each with its own manifest and checkpoint, so a large site resumes by
list instead of restarting:

```python
from office365.migration import MigrationSession, MigrationTask

session = MigrationSession().register(context=target_ctx)
session.add_site_task(
    task=MigrationTask.sharepoint(source_site_url, target_site_url, migrate_all=True),
    exclude=["Site Assets"],
    manifest_dir="state/manifests",
    checkpoint_dir="state/checkpoints",
)
session.start()
```

The registered `context` is the **target**; a source on a different site
collection in the **same tenant** is reached through an authenticated clone
(`ClientContext.clone`), reusing the registered credentials. Document libraries
use the file adapters, other lists use the record adapters. Hidden lists,
SharePoint infrastructure templates, and non-deletable system lists are skipped.

Target lists are created on demand (by title, with the source template type) and,
by default, each list's **columns, content types and views are replayed** from
the source before content is copied (`provision_structure=True`) — the same
snapshot/replay used by `capture_list_structure` / `provision_list_structure`
(below). Pass `provision_structure=False` to only create the containers. The
server-side Migration API path is per-library and not supported for a whole-site
task.

### Capturing list structure

`capture_list_structure(sp_list)` reads a list's **columns** (with `SchemaXml`
prepared for `CreateFieldAsXml`), **content types** (with their ordered field
links), and **views** (with their ordered columns) into a read-only,
JSON-serializable `ListStructure` snapshot. Built-in/system and framework
columns, hidden content types, and hidden/personal views are skipped, and only
GET requests are issued:

```python
import json

from office365.migration.sharepoint import ListStructure, capture_list_structure

sp_list = source_ctx.web.lists.get_by_title("Projects")
structure = capture_list_structure(sp_list)
print(structure.title, len(structure.fields), len(structure.content_types), len(structure.views))

with open("projects.structure.json", "w", encoding="utf-8") as fh:
    json.dump(structure.to_dict(), fh, indent=2)

with open("projects.structure.json", encoding="utf-8") as fh:
    restored = ListStructure.from_dict(json.load(fh))
```

A snapshot can be inspected, persisted, and later replayed.

### Provisioning list structure

`provision_list_structure(sp_list, structure)` replays a snapshot onto a target
list: it creates the missing columns from their `SchemaXml`, the custom content
types (matched by **name**), and the views, and turns content types on when the
snapshot says so. It is idempotent — running it again with the default
`on_conflict="skip"` is a no-op — and it executes the requests, so call it right
after the target list exists and before content is copied:

```python
from office365.migration.sharepoint import provision_list_structure

warnings = provision_list_structure(target_ctx.web.lists.get_by_title("Projects"), structure)
for warning in warnings:
    print("structure warning:", warning)
```

Two SharePoint Online REST limits are surfaced honestly rather than hidden:

- **Content type identifiers are not preserved.** The server assigns a content
type its own `Id` and ignores the requested one (at both list and web scope), so
content types are matched and recreated by **name**.
- **A fresh column cannot be attached to a custom content type.** Adding a field
link for a column that is not already inherited or auto-linked is rejected
(`Column '<name>' does not exist`). Those columns are skipped and returned in the
`warnings` list (and logged) instead of failing the whole provisioning.

Field-link **order** is restored only when at least one link was actually added.

## Fidelity

| Flag | Client-side runner | Server-side Migration API |
|---|---|---|
| `preserve_timestamps` | best-effort (`Created`/`Modified`) | full |
| `preserve_permissions` | best-effort (same-tenant ACL copy) | full |
| `preserve_versions` | ✗ (raises) | full |

REST cannot restore version history, so `preserve_versions` always requires the
server-side API. The other two are applied client-side **when the adapters
support them** — the runner fails fast otherwise, rather than silently migrating
without the requested fidelity:

```python
MigrationJob(source, target, MigrationOptions(preserve_timestamps=True, preserve_permissions=True))
```

- **Timestamps** — the SharePoint library target restores `Created`/`Modified`
  via `ValidateUpdateListItem` (the same path as `ListItem.system_update`).
- **Permissions** — the source reads the item's `role_assignments`; the target
  breaks inheritance and recreates them, resolving principals by login name and
  roles by name. This is a **same-tenant** copy; cross-tenant identity mapping is
  not implemented.

Adapters opt in by implementing optional hooks:
`DataSource.read_permissions(item)`, `DataTarget.apply_timestamps(item)`, and
`DataTarget.apply_permissions(item, permissions)`.

To see what a pair will actually honor **before** a run, ask for a report —
`MigrationJob.fidelity()`, or `MigrationSession.fidelity()` for every task:

```python
report = MigrationJob(source, target, MigrationOptions(preserve_timestamps=True)).fidelity()
print(report.summary())  # "not requested: permissions, versions | UNSUPPORTED: timestamps"
print(report.to_dict())  # JSON-serializable, for reports/status
```

The report is informational (it never raises); the run itself still fails fast on
an unhonorable flag. `MigrationSettings.preserve_timestamps` / `.preserve_permissions`
feed the matching options into every session task by default.

## Server-side migration (full fidelity)

For version history and true ACL fidelity, content is packaged and ingested
server-side. The package layer builds the Migration API manifest XML
(`Manifest.xml` / `ExportSettings.xml` / `SystemData.xml` / `UserGroup.xml`)
from a document library's files and folders:

```python
from office365.migration import MigrationJob
from office365.migration.adapters.filesystem import FileSystemSource
from office365.migration.sharepoint.package_target import SharePointPackageTarget

# Provision SharePoint-owned Azure containers (SAS URIs + encryption key)
containers = ctx.site.provision_migration_containers().execute_query().value

target = SharePointPackageTarget(
    ctx.site,
    web_id,
    content_uri=containers.DataContainerUri,
    manifest_uri=containers.MetadataContainerUri,
    encryption_key=containers.EncryptionKey,
)
job = MigrationJob(FileSystemSource("src"), target)
job.plan()
job.run()  # stages the package and submits the ingestion job
target.monitor()  # polls GetMigrationJobProgress
```

`MigrationServerJob` can also be driven directly (`submit` / `submit_encrypted` /
`progress` / `status_fn` / `monitor`).

With `encryption_key` set, the staging AES-256-CBC encrypts every content and
manifest blob (unique random IV, stored as the base64 `IV` blob property) — which
SharePoint-provided containers require. For your own (BYO) containers, omit it and
use `Site.create_migration_job` instead of the encrypted variant.

The builder covers the **document-library subset** — webs, lists, folders, files,
and file versions. The generated XML follows the documented format but is **not
yet verified against a live tenant** (see `office365.migration.package`).

## Storage & vendor neutrality

Server-side ingestion is the only leg that needs Azure — and that is Microsoft's
requirement, not ours. The Migration API reads content/manifest blobs from Azure
Blob Storage; it cannot read from local disk or S3.

| Move | Path | Azure? | Fidelity |
|---|---|---|---|
| M365 → filesystem / S3 / other | client-side adapters | no | content + best-effort timestamps/ACLs |
| filesystem / other → M365 | client-side adapters | no | content + best-effort |
| filesystem / other → M365 | server-side Migration API | **yes** | versions, ACLs, authors |
| M365 → M365 | either | only for server-side | — |

### You don't need an Azure account

`Site.provision_migration_containers()` provisions **SharePoint-owned** containers —
*no extra cost, and without the need to manually set up in the Azure admin
console*. It returns the container URIs (with SAS tokens) and the encryption key.
The `[azure]` extra is **only the client library** used to push blobs into
whatever container you were handed — it is not an Azure subscription:

```bash
pip install office365-rest-python-client[azure]
```

### Step by step

```python
from office365.migration import MigrationJob
from office365.migration.adapters.filesystem import FileSystemSource
from office365.migration.sharepoint.package_target import SharePointPackageTarget

# 1. Provision SharePoint-owned containers (no Azure account needed)
containers = ctx.site.provision_migration_containers().execute_query().value
#    containers.DataContainerUri     -> content container (SAS)
#    containers.MetadataContainerUri -> manifest container (SAS)
#    containers.EncryptionKey        -> AES256CBC key

# 2. Point the target at the containers (staging is swappable — see below)
target = SharePointPackageTarget(
    ctx.site,
    web_id,
    content_uri=containers.DataContainerUri,
    manifest_uri=containers.MetadataContainerUri,
    encryption_key=containers.EncryptionKey,
)

# 3. Migrate: items -> manifest XML -> staged blobs -> submitted job
job = MigrationJob(FileSystemSource("src"), target)
job.plan()
job.run()
print(target.job_id)

# 4. Poll GetMigrationJobProgress until the job is terminal
target.monitor()
```

### The `Staging` seam

The package (documented XML + content blobs) is vendor-neutral bytes; **where they
land is a strategy**. Pass `staging=` to `SharePointPackageTarget`:

- `FileSystemStaging` — writes `manifest/` + `content/` to disk (no Azure; tests,
  inspection, or handing the package to another uploader);
- `BlobStaging` — Azure Blob (what `create_staging(...)` returns today);
- `create_staging(content_url, manifest_url)` — the factory that picks a backend by
  container host. It is the extension point: a future S3 / Azure Files staging
  slots in here without changing callers.

```python
from office365.migration.package import FileSystemStaging

# Build + write the package to disk (no Azure, no submit)
target = SharePointPackageTarget(ctx.site, web_id, staging=FileSystemStaging("pkg/content", "pkg/manifest"))
package = target.stage()
```

### When you don't need Azure at all

If you don't need version history or ACLs, skip the package entirely and use the
client-side adapters — they move content over REST in either direction, including
to the filesystem (see [Fidelity](#fidelity)).

## Verification & reports

`job.verify()` reconciles item counts and spot-checks content checksums, and
`job.export_reports(dir)` writes Summary/Item/Failure reports as CSV + JSON.

## See also

- [Data pipeline](data-pipeline.md) — tabular import/export
- [Large lists](large-lists.md) — thresholds that shape a migration plan
- [Limits](limits.md) — the service limits the toolkit respects
