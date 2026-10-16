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

## Client-side vs server-side

Two engines ship in this package. They are **not interchangeable** — they move
different content and deliver different fidelity:

- **Client-side** (`SharePointLibrarySource/Target`, `SharePointListSource/Target`)
  drives the ordinary SharePoint REST API item by item: files and folders, record
  lists and their attachments, and — via `capture_list_structure` /
  `provision_list_structure` — columns, content types, and views. No Azure.
- **Server-side** (`SharePointPackageTarget` + `MigrationServerJob`) builds a
  Migration API package in Azure Storage and submits a bulk ingestion job. It is
  the only path that can carry version history.

| Axis | Client-side (REST) | Server-side (Migration API) |
|---|---|---|
| Content | files + folders, **record lists + attachments**, list structure | **document libraries** (files/folders + version history) |
| Version history | ✗ | ✓ the runner reads each file's history and the package carries `<Versions>` |
| Authors / ModifiedBy | not preserved | ✓ applied from `UserGroup.xml` (integer principal id, matched by PUID) |
| Permissions | library: best-effort same-tenant ACL; list: ✗ | best-effort same-tenant ACL — **resolved users only** (groups / unresolved principals skipped with a warning) |
| Columns / content types / views | captured + provisioned over REST | **not emitted** by the builder today |
| Azure Storage | not needed | required (SharePoint-owned containers; no Azure account) |
| Throughput | per-item HTTP, throttle-aware, resumable | bulk server-side ingestion; poll a job |
| Verification | `job.verify()` — counts, md5 (Office files compared canonically), identity marker | job progress/events + `diagnose()` (no content diff) |

**Choose client-side** when you need list items, structure, or verification, and
can tolerate REST throughput. **Choose server-side** when the content is a document
library and version history matters. **Mix them**: provision the target's columns,
content types, and views client-side, then hand the library's files to the server
side.

> The server-side engine reuses the same `MigrationJob` / runner. Version history
> is preserved automatically when the source exposes `read_version_history` (the
> SharePoint library source) and the target is `SharePointPackageTarget` — so
> `preserve_versions` is honored there and rejected only on the client-side REST
> target. Authorship and resolved-user ACLs are applied on the server-side path
> too — see [Fidelity](#fidelity).

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

### Migrating list items

`SharePointListSource` projects every readable field of each item into the record
payload (excluding the `AttachmentFiles` navigation, which is captured separately).
Attachments become their own manifest items and are uploaded to the matching parent
after the records have been flushed.

To pair source and target items for verification — and to make the default `SKIP`
policy idempotent, so re-running does not duplicate records — the target stamps
every item with a source-id marker, `MigrationSourceId` by default. This adds a
real column to every migrated list; pass `identity_field=None` to
`SharePointListTarget` to opt out (verification then falls back to target ids and
can no longer reconcile a re-run).

Two honest limits remain:

- Record **content** is verified over the item's scalar content columns: the
  source fingerprint and the target read-back hash the same fields, so a value
  difference is a real `mismatch`. Server-assigned identity (`Id`/`GUID`), the
  separately-checked timestamps/authorship/permissions, the remapped
  `ContentTypeId`, and version bookkeeping are excluded by design. **Typed
  columns** (lookup/person/Managed Metadata) are dropped rather than remapped, so
  they are outside the content check — the target write warns when they are
  skipped.
- Per-item **timestamps/permissions/authorship**
  (`preserve_timestamps`/`preserve_permissions`/`preserve_authorship`) are applied
  by the list adapters on a best-effort basis: timestamps and authorship are
  written with `ValidateUpdateListItem`; only items with a **unique** source ACL
  are copied. Unresolved principals and unhonorable facets surface as
  `mismatches`/`unverifiable` in the post-run verification, never as a silent
  drop.

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
`provision_structure=False` to `add_task` / `add_site_task` to skip that. This
replay happens even when `MigrationSettings(use_migration_api=True)` routes
content through a server-side package, because the package builder does not emit
columns, content types, or views today — the target's structure is still captured
and replayed over REST first.

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

**Subsites are not migrated by default.** They are detected and named in
`session.warnings()`, so a whole-site run never quietly ignores them. Pass
`include_subwebs=True` to mirror the source subsite tree on the target and migrate
their lists too: each missing target subsite is created from the source's title
and web template, and every web is addressed through its own clone (a subweb's
sub-collections resolve against the context root otherwise).

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

  Because the identifier changes, an item's `ContentTypeId` (which carries the
  *source* identifier) no longer exists on the target, and SharePoint silently
  coerces it to the list's default content type. `content_type_map` captures the
  source→target identifier so the record projection can rewrite it:

  ```python
  from office365.migration.map import ContentTypeMap

  mapping = {}
  provision_list_structure(target_list, structure, content_type_map=mapping)
  target = SharePointListTarget(target_list, content_type_map=ContentTypeMap(mapping))
  ```

  The whole-site (`resolve_site_task`) and single-list resolvers build and apply
  the map automatically, so a task-based migration needs nothing extra.

- **A fresh column cannot be attached to a custom content type.** Adding a field
link for a column that is not already inherited or auto-linked is rejected
(`Column '<name>' does not exist`). Those columns are skipped and returned in the
`warnings` list (and logged) instead of failing the whole provisioning.
Captured content types also name every built-in/SharePoint-owned column
(`Title`, `FileLeafRef`, framework columns) that capture deliberately does not
recreate; those are left to the target list's own defaults rather than sent as
guaranteed link failures.

A structure-provisioning warning is also recorded on the resolved target adapter,
so a whole-site session reports it through `session.warnings()` instead of only in
the log.

Field-link **order** is restored only when at least one link was actually added.

## Fidelity

| Flag | Client-side runner | Server-side package |
|---|---|---|
| `preserve_timestamps` | best-effort (`Created`/`Modified`) | ✓ carried per manifest object (`TimeCreated`/`TimeLastModified`) |
| `preserve_authorship` | best-effort (`Author`/`Editor` via `EnsureUser`) | best-effort — resolved PUID users only |
| `preserve_permissions` | best-effort (same-tenant ACL copy) | best-effort — resolves users by PUID; groups / unresolved principals skipped |
| `preserve_versions` | ✗ (raises) | ✓ the runner reads history into the package's `<Versions>` |

The server-side package target is the only one that preserves version history: the
runner reads each file's older versions (`source.read_version_history`) and passes
them to `PackageBuilder.add_file`, which the Migration API promotes into a real
version history. Timestamps ride the same package; authorship (`UserGroup.xml`
principal ids) and resolved-user ACLs (`DeploymentRoles` +
`DeploymentRoleAssignments`) are applied by the service (see
[Client-side vs server-side](#client-side-vs-server-side)). REST cannot restore
version history, so `preserve_versions` always requires a Migration API package and
fails fast on the client-side target. Timestamps and permissions are applied
client-side **when the adapters support them** — the runner fails fast otherwise,
rather than silently migrating without the requested fidelity:

```python
MigrationJob(source, target, MigrationOptions(preserve_timestamps=True, preserve_permissions=True))
```

- **Timestamps** — the client-side targets restore `Created`/`Modified`
  via `ValidateUpdateListItem` (`datesInUTC=True`; the same path as
  `ListItem.system_update`).
- **Authorship** — the client-side targets restore `Author`/`Editor` by resolving
  each source principal through `web.ensure_user` and writing a `FieldUserValue`.
  Principals `EnsureUser` cannot resolve are skipped (the verification reports the
  resulting mismatch); the server-side package emits `UserGroup.xml` ids instead.
- **Permissions** — the source reads the item's `role_assignments`; the target
  breaks inheritance and recreates them, resolving principals by login name and
  roles by name. Only items with an **unique** ACL are copied — the REST surface
  reports inherited role assignments too, and copying those would break
  inheritance on every item and duplicate the parent ACL. On the server-side
  package target, `preserve_permissions=True` emits
  `DeploymentRoles`/`DeploymentRoleAssignments` for **resolved users** (matched by
  PUID; groups/unresolved principals are skipped with a warning). Both are
  **same-tenant**; cross-tenant identity mapping is not implemented.

Adapters opt in by implementing optional hooks: `DataSource.read_permissions(item)`,
`DataTarget.apply_timestamps(item)`, `DataTarget.apply_authorship(item)`, and
`DataTarget.apply_permissions(item, permissions)`. To *verify* that the requested
fidelity actually landed, the read counterparts are used too:
`read_metadata(item)` (comparable `created`/`modified`/`size_bytes`) and
`read_authorship(item)` on both sides, and `read_permissions(item)` on the target.
Both the document-library and record-list REST adapters implement all of them.

To see what a pair will actually honor **before** a run, ask for a report —
`MigrationJob.fidelity()`, or `MigrationSession.fidelity()` for every task:

```python
report = MigrationJob(source, target, MigrationOptions(preserve_timestamps=True)).fidelity()
print(report.summary())  # "not requested: permissions, versions | UNSUPPORTED: timestamps"
print(report.matrix_summary())  # "content=delivered, versions=unsupported, ..."
print(report.to_dict())  # JSON-serializable, for reports/status
```

The report is informational (it never raises); the run itself still fails fast on
an unhonorable flag. `MigrationSettings.preserve_timestamps` / `.preserve_permissions`
feed the matching options into every session task by default.

### Fidelity matrix

`report.dimensions` reports **every** dimension the engine models — each
`delivered`, `best-effort`, `unsupported`, or `handoff` — so a gap is never
implicit. The matrix is probed from the adapter pair's capability attributes
(`supports_versions`, `supports_authorship`, `supports_attachments`) and optional
hooks (`apply_timestamps`, `read_permissions`/`apply_permissions`); a non-delivered
dimension always carries a reason in `report.dimension_notes`. The table below is
the shipped pairs' expected output.

| Dimension | Library → package | Library → REST | List → REST |
|---|---|---|---|
| Content | delivered | delivered | delivered |
| Versions | best-effort (history content; per-version author/time not carried) | unsupported | unsupported |
| Created/Modified | delivered | delivered | delivered |
| Author/Editor | best-effort (resolved PUID users only) | best-effort (resolved users only) | best-effort (resolved users only) |
| Permissions | best-effort (same-tenant, resolved users) | best-effort (same-tenant) | best-effort (same-tenant, unique ACLs only) |
| Attachments | n/a | n/a | delivered (list items) |
| Columns / content types / views | unsupported by the adapters — replay them with `provision_list_structure` | same | same |
| Lookup / Person / MMD values | unsupported (values copied verbatim; remap not implemented) | same | same |
| Check-out / draft / approval state | unsupported | unsupported | unsupported |
| Navigation / pages / web parts | handoff (detect and remediate out of band) | same | same |
| Sharing links | unsupported (following tenant policy; not recreated per item) | same | same |

> Columns, content types, and views are deliberately *not* carried by the item
> adapters: they are schema, and the SharePoint resolver replays them over REST
> with `provision_list_structure` (whole-site and single-list resolution do this
> by default). The matrix reports the adapter-level truth.

## Server-side migration

For version history, content is packaged and ingested server-side. The package layer builds the Migration API manifest XML
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

The builder covers the **document-library subset** — the library, folders, files,
and file versions. Version history is carried through `MigrationJob` whenever the
source exposes `read_version_history` (the SharePoint library source does); the
runner reads it into each item and the package emits `<Versions>`. It emits **no**
columns, content types, or views: provision those client-side first (see
[Provisioning list structure](#provisioning-list-structure)). The source also
skips the library's own `Forms/` scaffolding, which SharePoint recreates on the
target. The end-to-end import is validated against a live tenant for
file/folder content, **version history**, **authorship** (`Author`/`ModifiedBy`),
and — with `preserve_permissions=True` — **same-tenant ACLs for resolved users**.
Each `UserGroup.xml` user carries its PUID (`SystemId`); each granted level is
emitted as a `DeploymentRoles` `<Role>` with a fresh non-system id and a decimal
`PermMask` and is matched by `Title` to the target's existing permission level, so
no duplicate is created. Groups and principals that cannot be resolved to a PUID
are skipped and reported as warnings.

## Storage & vendor neutrality

Server-side ingestion is the only leg that needs Azure — and that is Microsoft's
requirement, not ours. The Migration API reads content/manifest blobs from Azure
Blob Storage; it cannot read from local disk or S3.

| Move | Path | Azure? | Fidelity |
|---|---|---|---|
| M365 → filesystem / S3 / other | client-side adapters | no | content + best-effort timestamps/ACLs |
| filesystem / other → M365 | client-side adapters | no | content + best-effort |
| filesystem / other → M365 | server-side Migration API | **yes** | versions + authorship (ACL best-effort) |
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

`job.verify()` returns a `VerificationReport` and `job.export_reports(dir)`
writes Summary/Item/Failure reports as CSV + JSON. Verification is layered and
explicit about what it could not confirm:

| Check | When | Finding bucket |
|---|---|---|
| Presence (expected vs found paths) | always | `missing` / `extra` |
| Content checksums | always, on a `spot_checks` sample | `mismatches` (or `unverifiable` if a side exposes no comparable hash) |
| Timestamps (`Created`/`Modified`) | when `preserve_timestamps` was requested | `mismatches` / `unverifiable` |
| Authorship (`Author`/`Editor`) | when `preserve_authorship` was requested | `mismatches` / `unverifiable` |
| Permissions | when `preserve_permissions` was requested | `mismatches` / `unverifiable` |
| Versions | when `preserve_versions` was requested | always `unverifiable` over REST |

For SharePoint list items the source and target are paired by the
`MigrationSourceId` marker (see [Migrating list items](#migrating-list-items));
attachment presence *and* content (md5) are checked, and each record's scalar
content columns are hashed on both sides, so a field-value difference is a real
`mismatch` rather than an `unverifiable` caveat.

Office Open XML documents (`.docx`/`.xlsx`/`.pptx`/…) that md5-differ are compared
canonically before being called a mismatch: SharePoint re-serializes them on
upload (document property promotion/demotion rewrites `docProps/`, `customXml/`
and adds `[trash]/` parts), so a byte hash of a client-side REST round-trip is not
stable. If every part SharePoint does not own matches, the file is reported as an
`unverifiable` caveat rather than a false mismatch; a difference in any other part
is still a real `mismatch`.

Presence ignores each library's SharePoint-owned scaffolding on **both** sides —
`Forms/`, `desktop.ini`, and on Site Assets the `__siteIcon__.png` site icon and
the auto-provisioned `<web title> Notebook` folder — so it is neither migrated nor
reported as missing/extra.

A requested check that could not run lands in `report.unverifiable` — `report.ok`
is then still True when nothing contradicted it, but `report.complete` is False.
This is deliberate: a *partial* verification is never silently reported as a pass.

```python
report = job.verify()
print(report.summary())  # "OK | ..." / "PARTIAL | ..." / "MISMATCH | ..."
print(report.to_dict())  # JSON-serializable evidence
assert report.complete
```

### Verifying list structure

Content validation never looks at the *container*. To confirm that a target list
reproduces the source's columns, content types and views (read-only; issue GETs
only), compare the two captured snapshots:

```python
from office365.migration.sharepoint import verify_list_structure

report = verify_list_structure(source_list, target_list)
print(report.summary())  # "MISMATCH | Projects | columns: 2, content types: 1, views: 0, field links: 1"
if not report.ok:
    print(report.to_dict())
```

Only *missing* structure is reported: a freshly created target list legitimately
carries extra built-in columns, content types and views, so "extra" entries are
not findings. Field links that could not be attached (the REST limit described
above) show up as `missing_field_links`.

## See also

- [Data pipeline](data-pipeline.md) — tabular import/export
- [Large lists](large-lists.md) — thresholds that shape a migration plan
- [Limits](limits.md) — the service limits the toolkit respects
