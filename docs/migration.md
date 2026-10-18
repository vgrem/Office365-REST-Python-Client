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
  `provision_list_structure` — columns, content types, views, list container
  settings and column/view formatting JSON. No Azure.
- **Server-side** (`SharePointPackageTarget` + `MigrationServerJob`) builds a
  Migration API package in Azure Storage and submits a bulk ingestion job. It is
  the only path that can carry version history.

| Axis | Client-side (REST) | Server-side (Migration API) |
|---|---|---|
| Content | files + folders, **record lists + attachments**, list structure | **document libraries** (files/folders + version history) |
| Version history | ✗ | ✓ the runner reads each file's history and the package carries `<Versions>` |
| Authors / ModifiedBy | not preserved | ✓ applied from `UserGroup.xml` (integer principal id, matched by PUID) |
| Permissions | best-effort same-tenant ACLs at all three container scopes: **items**, a **list's own ACLs** and **web permission levels, groups and role assignments** (with `--preserve-permissions`) | best-effort same-tenant ACL — **resolved users only** (groups / unresolved principals skipped with a warning) |
| Columns / content types / views / formatting | captured + provisioned over REST (column + view `CustomFormatter` JSON included) | **not emitted** by the builder today |
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

### Delta re-runs

A re-run reconciles *content*, not *drift*: an item deleted at the source leaves
an orphan on the target, and a rename or move looks like a brand-new item — the
old target copy stays where it was, so the re-run duplicates it. Point a job at
the manifest a previous run persisted (`manifest_path=`, or `manifest_dir=` for a
whole-site task) and it diffs that plan against the fresh one before replacing it:

```python
job = MigrationJob(source, target, manifest_path="state/manifests/docs.json")
job.plan()  # the delta is computed here, before the plan is replaced
print(job.delta.summary())  # delta vs 412 planned item(s): 1 new, 2 gone, 3 moved, 0 changed
print(job.delta.is_stale)  # True — a deletion or a move cannot converge on its own
for note in job.delta.notes():  # ready-to-print, sampled to five paths per kind
    print(note)
```

`job.delta` (a `DeltaReport`) names four kinds of drift: `added` (in the fresh
plan only), `missing` (planned before, gone from the source now), `moved` (the
same source identity at a different path) and `changed` (same path, different
modification time — under the default `skip` policy an existing target copy is
left as it was). `session.delta()` returns one report per task, and
`MovedItem`/`compute_delta` are exported for a report of your own.

Detection is **read-only**: nothing is deleted on the target, because a target may
legitimately hold content the copy did not put there (`extra` in the verification
report is the same orphan seen from the other side). The limits are stated instead
of guessed at: a move is only recognizable when the source exposes a stable
identity (`MigrationItem.source_id` — a SharePoint file's `UniqueId`), so a
renamed *folder* is reported as one missing path plus the moved paths of its
children, and a list item is keyed by its source item id — retitling it is a
`changed` item, never a move.

## Adapters

| Adapter | Direction | Content |
|---|---|---|
| `FileSystemSource` / `FileSystemTarget` | both | files + folders |
| `JsonFileSource` / `JsonFileTarget` | both | record payloads (one JSON file per item) |
| `SharePointLibrarySource` / `SharePointLibraryTarget` | both | files + folders (recursive) + folder column values and system metadata |
| `SharePointListSource` / `SharePointListTarget` | both | list items as records |
| `MailFolderSource` / `MailExportTarget` | export | mail as a portable EML tree (`office365.migration.outlook`) |
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
  columns** are remapped rather than dropped where the target can: a **Lookup**
  value is translated from the source list's item id to the matching target item
  through each migrated list's `MigrationSourceId` marker, and a **Person** value
  is carried as a login name and resolved to the target's own site-user id with
  `EnsureUser`. **Single- and multi-value** Lookup/Person columns are covered
  (a multi-value column is written as `{"results": [...]}`). **Managed Metadata**
  values are carried by **term id** only — `Label` and the site-local `WssId` are
  cosmetic and are not compared: a single-value column is written as a typed
  `SP.Taxonomy.TaxonomyFieldValue`, a multi-value column through its hidden note
  companion (`-1;#Label|guid;#...`, the only shape the server accepts), and both
  sides are verified by a sorted term-id list. Structure provisioning recreates a
  taxonomy column with `TaxonomyField.create(...)` against the same term set, so
  it binds to the **target** web's `TaxonomyHiddenList` instead of the source's.
  The term store itself is not migrated: a term absent on the target is rejected
  by the server, so this is a same-tenant (or pre-provisioned store) capability.
  A value that cannot be resolved (a lookup into a list outside this migration, a
  term absent from the target store, an unknown login) is dropped with a warning
  rather than written wrong. Typed values in **hidden** columns are dropped too:
  structure provisioning does not replicate hidden columns, so there is no target
  column to write them to. A **multi-choice** column needs no remapping — it holds
  plain strings — but its shape does: a live read returns the selection as a
  positional mapping, so the source records it as a bare list and the target wraps
  it as `{"results": [...]}` for the create. The read-back mapping is canonicalized
  to the same list before hashing, which makes a lost selection a real `mismatch`;
  only `TypeAsString == "MultiChoice"` counts as multi-value, because a
  `Type="Choice" Mult="TRUE"` column keeps that flag while storing a single value.
  A **Hyperlink** value travels as the `{"Url", "Description"}` object both sides
  read and a create accepts as-is. Other value objects — an image/thumbnail, a
  geolocation point — are still dropped with a warning instead of being sent in a
  shape the server may reject.
- **Document library folders** are list items too, so their own column values — a
  document set's metadata, a managed folder's department — travel as the folder's
  payload. A library adapter built with its library (`sp_list=`, which the site
  resolvers always pass) reads them with an **explicit projection** of the
  folder's writable columns — a `*` read fails on a library, which has no
  `Attachments` column — and the target MERGEs them onto the folder's list item
  once the structure exists. *Writable* means non-hidden, not
  underscore-prefixed (SharePoint's storage columns are not projectable), not
  read-only and not a computed type (`Computed`/`File`/`Attachments`/
  `WorkflowStatus`, i.e. `LinkFilename`, `DocIcon`, …); the target drops the same
  columns from its read-back so the fingerprints are comparable. The folder's
  `ContentTypeId` is carried (a `MERGE` does change a folder's content type —
  live-checked) but stays out of the fingerprint, as for item records, and an
  empty value counts as absent on both sides. A failed value write is a warning,
  never fatal: the folder's structure matters more than its metadata. Verification
  samples folders for the content check alongside items, and only when both
  adapters were built with their library — a filesystem pair carries no folder
  values and stays silent rather than reporting them as unverifiable.
- A folder's **own system metadata** — `Created`/`Modified` and `Author`/`Editor` —
  is carried as well: a folder is a list item with a timestamp just like a file, so
  the same diff reports it. It is read back from the **folder resource** on both
  sides (the recursive listing already returns tz-aware timestamps, while a list
  item's form values are web-local naive strings and would never compare equal).
  Two live-probed details shape the implementation:
  - The stamps are applied in a **post-content pass**, after all content has been
    written, not item by item: a folder's `Modified` follows its children, so
    uploading a file into it — or creating a subfolder — resets it to now. Stamping
    a parent before its subtree exists silently loses the value.
  - An **existing** folder is *not* skipped the way an existing file is. A folder
    holds no content to duplicate, and a resumed run has to re-apply its metadata,
    otherwise a re-verify reports every untouched folder as drifted. Files keep the
    skip: a re-run neither re-uploads nor re-stamps content that is already there.
  Folder fidelity rides on the same `supports_folder_records` capability as the
  folder values, so a filesystem pair stays silent instead of reporting it as
  unverifiable.
- A **document library file's approval state** (content moderation) is carried when
  the library enables it: the source reads `OData__ModerationStatus`/
  `OData__ModerationComments` alongside the author ids (one extra projection on the
  read it already does) and the target restores them. Only a **draft/pending or
  rejected** file needs this — a fresh upload lands *approved* — so an approved file
  costs no extra write. Two live-probed details shape the implementation:
  - It is a **separate, final write**, not folded into the timestamp one: a document
    rejects a moderation change together with other properties (*You cannot change
    moderation status and set other item properties at that same time*).
  - Every `ValidateUpdateListItem` write on a document **approves** it (whatever its
    `bNewDocumentUpdate` flag), which is exactly why the state has to be written
    last. The moderation write still moves the list item's own `Modified` (it cannot
    be combined with anything else), so a draft file reports the *migration* time
    there — its `File.TimeLastModified`, the value the metadata diff compares, keeps
    the source timestamp.
  A failed state write is a warning, never fatal.
- A **checked-out file** is copied from its last *checked-in* version, because that
  is all REST exposes — the author's in-progress edits live in the check-out and
  never reach a reader. Carrying the check-out itself is not an option either: it
  would leave the copy locked by the migrating app. The copy is therefore faithful
  to the source but incomplete, and **verification cannot notice** — it compares the
  same read on both sides — so the source reports it instead: one warning per run,
  naming the files (`N checked-out file(s) were copied from their last checked-in
  version (in-progress edits are not visible over REST): …`). The `CheckoutUser`
  detection rides the single item read that already supplies the author ids.
- A file on an **un-published (minor) version** is copied as its **draft**, and that
  is the honest half of the story: REST returns the draft content (live-probed — a
  file at `1.1` returns the draft, not the published `1.0`), so the copy matches
  what the source reports, while the published version the draft supersedes stays
  behind — client-side SP→SP does not restore version history. Verification again
  compares the same read and cannot notice, so the source reports it: one warning
  per run naming the files (`N file(s) are on an un-published (minor) version: the
  draft content is copied, the published version it supersedes is not (version
  history is not preserved): …`). The signal rides the file listing the source
  already reads (`MinorVersion`): a published file is `x.0`, a draft `x.n` with
  `n > 0`. The draft *state* itself is not lost — the approval state carries it
  when the target library moderates — so the warning names the version history,
  not the content.
- Per-item **timestamps/permissions/authorship**
  (`preserve_timestamps`/`preserve_permissions`/`preserve_authorship`) are applied
  by the list adapters on a best-effort basis: timestamps and authorship are
  written with `ValidateUpdateListItem`; only items with a **unique** source ACL
  are copied. Unresolved principals and unhonorable facets surface as
  `mismatches`/`unverifiable` in the post-run verification, never as a silent
  drop.

## Migrating mail

A mailbox export is the same job as a file migration: `MailFolderSource`
enumerates messages as items (one per message, its envelope carried in
`item.metadata`), and `MailExportTarget` writes a portable EML tree.

```py
from office365.migration import MigrationJob
from office365.migration.outlook import MailExportOptions, MailExportTarget, MailFolderSource

folder = client.me.mail_folders["inbox"].get().execute_query()
job = MigrationJob(
    MailFolderSource(folder, MailExportOptions(include_subfolders=True)),
    MailExportTarget("./mailbox-export"),
)
job.plan()
job.run()
print(job.verify().summary())  # each .eml's MD5 vs the source message's MIME
```

The target layout:

```text
<root>/Inbox/2024-03-01_Quarterly-report-Q1_cb65ad88.eml   # RFC 822 bytes
<root>/Inbox/2024-03-01_Quarterly-report-Q1_cb65ad88.json  # sidecar record
<root>/Inbox/Archive/2023-12-24_Old-thread_1f9c07aa.eml
<root>/manifest.jsonl                                      # one sidecar per line
```

Names are derived from the message (`date_subject_id-digest.eml`), not from the
enumeration order, so a re-run lands on the same paths and skips what is already
there. The sidecar carries what MIME cannot — Graph ids, read state, Outlook
categories, conversation id, folder path — and `manifest.jsonl` is what a later
import reads to restore them.

Three honest limits:

- **Attachments are inside the MIME.** They are part of the message, so they are
  not separate manifest items and not separately verified.
- **The MIME body is fetched per message.** `Message.get_content()` is batchable
  since 3.3.0, so batching those reads is a tuning step, not a redesign.
- **Drafts may have no `internetMessageId`.** Those are keyed by Graph id, which
  changes if the draft moves — a re-run then reports a second copy rather than
  overwriting the first.

For a pre-migration inventory (folder counts, large-folder flags) use
`MailboxAssessor`; for the mailbox-wide move into Exchange, the Exchange
migration service ingests this EML tree — the toolkit produces the artefact, it
does not wrap the service. The [example](https://github.com/vgrem/office365-rest-python-client/tree/master/examples/outlook/migration/export/README.md)
shows the flags (`--flat`, `--no-drafts`, `--preserve-timestamps`).

### Importing an EML tree

The inverse is the same job with the adapters swapped: `EmlTreeSource` reads the
`.eml` files (the sidecar becomes the item's envelope) and `MailboxTarget` writes
each message through Graph's MIME import, recreating the folder chain.

```py
from office365.migration import MigrationJob
from office365.migration.outlook import EmlTreeSource, MailImportOptions, MailboxTarget

inbox = client.me.mail_folders["inbox"].get().execute_query()
job = MigrationJob(EmlTreeSource("./mailbox-export"), MailboxTarget(inbox, MailImportOptions()))
job.plan()
job.run()
print(job.verify().summary())  # semantic digest, not bytes: Exchange re-serializes MIME
```

- **The export's top directory is the target folder.** Directories below it are
  created under the target using the sidecar's `folder_display_path`, so a folder
  called `All Mail` does not come back as `All-Mail`. `MailImportOptions(root_name=...)`
  nests the whole tree one level deeper.
- **Idempotent.** `exists()` matches on `internetMessageId` inside the target folder,
  so a resumed or re-run job skips what it already delivered instead of duplicating
  it — Exchange itself accepts duplicate `Message-ID`s with distinct ids.
- **Flags MIME cannot carry are replayed** (one `PATCH` per message, only when the
  value differs): read state, Outlook categories, importance.
  `restore_read_state=False` / `restore_categories=False` turn that off.

Four honest limits, all Exchange's rather than the adapter's:

- **An imported message is a draft.** Graph creates it with `isDraft: true` and
  ignores a PATCH that tries to clear it; only a real delivery (the Exchange
  migration service, IMAP `APPEND`) produces a non-draft.
- **`receivedDateTime` is the import time.** The original date survives in the `Date`
  header, which Graph exposes as `sentDateTime`, and that is restored for free.
- **Timestamps are not restorable**, so `preserve_timestamps` is refused up front by
  the runner rather than silently dropped.
- **4 MB per message.** Graph's MIME import caps the request body; a larger message
  needs an upload session, which this target does not use, so it raises rather than
  truncating.

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

**The settings surface is wider than the engine, and that is reported, not
implied.** `MigrationSettings` mirrors the cmdlet, but a client-side run cannot do
everything SPMT does — it does not migrate the term store, it cannot skip lists by
name, it carries no cross-tenant user map and it has no multi-round or Azure
storage plumbing. A knob that silently does nothing is a trap, so
`MigrationSettings.unhonored()` returns one ready-to-print note per setting whose
current value asks for behavior the engine does not implement (a setting whose
default *is* what the engine does stays silent), and a session appends them to
`session.warnings()` once:

```python
from office365.migration import MigrationSettings

MigrationSettings(skip_lists_with_name="Archive").unhonored()
# ['skip_lists_with_name=...'] plus the term-group default, which is never honored
```

Filter lists with the `include`/`exclude` arguments of `add_task`/`add_site_task`
instead, and migrate a term store with `StoreManager.export_tree()` /
`import_tree()`.

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

The recursion is **live-verified, end to end**: on a source site whose tree held
41 subsites, each missing target subsite was created from the source's web
template with its lists replayed (same titles and base templates), and a two-row
subsite list with a custom column came out with that column provisioned, both
values intact, the source/target verification reporting `OK`. Two limits are
worth naming: a web-scope **site content type** is not created — content types are
replayed only *through the lists that use them* (see *Provisioning list structure*
below) — and the mirrored webs are recreations, so
their ids, web-part data bindings and version history do not match the source's
(pages are copied per web, subwebs included — see *Site pages* below).

**Artifacts a copy cannot carry are named, never dropped silently.** Modern site
pages and classic wiki pages *are* copied (see *Site pages* below), but three
categories are outside what a client-side copy can produce — workflow
associations, InfoPath forms and business-data (BCS) external lists, plus any
page with no copyable body (a publishing page) — so the resolver
appends a handoff note for each one it finds (see
`detect_handoff(web, lists)` / `handoff_notes(handoff)` in
`office365.migration.sharepoint.handoff`, also exported from
`office365.migration.sharepoint`). Detection is cheap and best-effort: two extra
reads per web (the web's workflow associations, then one *projected* lists read
that carries each list's declared form URLs and its workflow associations), and a
detector that fails degrades to a note instead of aborting the run.

Target lists are created on demand (by title, with the source template type) and,
by default, each list's **columns, content types, views and container settings
are replayed** from the source before content is copied (`provision_structure=True`)
— the same snapshot/replay used by `capture_list_structure` /
`provision_list_structure` (below). Pass `provision_structure=False` to only
create the containers. The server-side Migration API path is per-library and not
supported for a whole-site task.

### Many lists at once

A whole-site task is a **queue of one job per list**, and `session.start()` walks
that queue serially by default. For a site of many small lists that is the
dominant cost, because each job pays its own fixed overhead — resolve the list,
ensure its container, replay its structure, read its items — and none of it
overlaps. Pass `concurrency` to run several jobs at once:

```python
from office365.migration.logging import ProgressReporter

reporter = ProgressReporter(interval=15, emit=print)
session.add_site_task(task=..., manifest_dir="state/manifests", progress=reporter)
session.start(progress=reporter, concurrency=4)
```

What is shared and what is not is deliberate:

| Per job | Shared by every job |
| --- | --- |
| pending-query queue, form digest, phase/stats | authentication context (single-flight token cache) |
| manifest + checkpoint (`<index>-<list>.…`) | HTTP transport: one connection pool |
| `ProgressReporter` counters (`derive`) | retry policy and `RateLimiter` (pacing) |

A `ClientContext` owns a single pending-query queue, so two jobs cannot use one
context concurrently. Each worker therefore gets a clone (`ClientContext.clone`,
which shares the auth context and transport *by reference*) and the adapters are
re-addressed on it (`MigrationJob.rebind()` → `adapter.rebind()`): a list is
looked up by id, a folder by server-relative path, which costs one read per
container and buys a run that is safe on threads. Context-free adapters
(`filesystem`, `json`) are shared unchanged, so a mixed session keeps working.

This changes *when* work happens, not *what* lands on the target: manifests,
checkpoints, conflict handling, verification, throttling accounting and warning
collection are the same, statuses are returned in registration order, and a job
that already completed is still skipped on a re-run. A task failure stops the
session as it does serially — after the in-flight jobs finish, so nothing is left
half-written. Keep `concurrency` and `--pace` together: the limiter is shared, so
pacing still bounds the whole run no matter how many workers are in flight.

**Resolution reports progress too.** `add_site_task(progress=...)` fires the same
`Progress` heartbeat the runner uses while the plan is resolved — `lists`, then
`containers` (per target container ensured), `structure` (per list replayed), and
the indeterminate `pages`, `navigation` and `branding` stages — so the run is not
silent between the inventory and the first copy.

### Capturing list structure

`capture_list_structure(sp_list)` reads a list's **columns** (with `SchemaXml`
prepared for `CreateFieldAsXml`), **content types** (with their ordered field
links), **views** (with their ordered columns) and **container settings**
(versioning and its limits, moderation, draft visibility, attachments, item-level
read/write security, list validation, and — for a document library — minor
versions and required check-out) into a read-only, JSON-serializable
`ListStructure` snapshot. Built-in/system and framework columns, hidden content
types, and hidden/personal views are skipped, and only GET requests are issued:

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
types (matched by **name**), and the views, applies the captured container
settings, and turns content types on when the snapshot says so. It is idempotent —
running it again with the default `on_conflict="skip"` is a no-op — and it
executes the requests, so call it right after the target list exists and before
content is copied:

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

- **Formatting is replayed after the columns and views exist, and reported when
  it does not take.** Column formatting (`Field.CustomFormatter`) and row
  formatting (`View.CustomFormatter`) are JSON blobs on the entity itself, so they
  are a `MERGE` each, written only when the target's differs. A *sealed* column
  accepts the `MERGE` and silently drops the value, so the pass reads both sides
  back and returns a warning (`column 'X' kept its own formatting`) instead of
  claiming success — verification compares the two blobs in its own `formatting`
  column. An **SPFx field customizer** (`ClientSideComponentId`) is a pointer into
  a deployed solution: it cannot work on a target that does not have that solution,
  so it is reported, never copied.
- **A fresh column cannot be attached to a custom content type.** Adding a field
link for a column that is not already inherited or auto-linked is rejected
(`Column '<name>' does not exist`). Those columns are skipped and returned in the
`warnings` list (and logged) instead of failing the whole provisioning.
Captured content types also name every built-in/SharePoint-owned column
(`Title`, `FileLeafRef`, framework columns) that capture deliberately does not
recreate; those are left to the target list's own defaults rather than sent as
guaranteed link failures.
- **Site columns are registered at web scope before any list is replayed.** A
  **site column** (one whose `Scope` is the web's server-relative URL, e.g.
  `/sites/team_in`, not the list's) used to be seen only *through the lists that
  use it*; `provision_list_structure` now has a web-level companion in the
  resolver: `provision_web_scope_columns` runs once per web, before the per-list
  replay, and creates every source site column the target web lacks. Ordering is
  the point — a list's `Fields` collection includes the site columns it inherits,
  so the replayed list then *reuses* the web column instead of minting a second,
  list-scoped copy of it. Each column is recreated from its source `SchemaXml`
  (`SourceID`/`Version` stripped by `Field.schema_xml_for_copy`, because
  SharePoint rejects a copied origin header), a lookup is repointed at the target
  list, and a managed-metadata column goes through `TaxonomyField.create` so it
  binds the *target* web's hidden taxonomy list and note field instead of the
  source's. The create is verified by presence afterwards: SharePoint Online
  registers the column and *then* raises `SPFieldValidationException` ("The object
  has been updated by another user since it was last fetched"), so the exception is
  not evidence of failure. Re-running is a no-op (`already present`).

  A **web-scope content type** is still not created. Content types are replayed
  per list, by name, description and group — SharePoint Online assigns the new
  content type its own identifier, so the source's `string_id` is not preserved —
  and attaching a *fresh* site column to a content type is impossible over REST
  anyway: `FieldLinks` rejects it (`Column '<name>' does not exist`) until the
  column is reachable from the list. A definition no migrated list uses is
  therefore still missing, and its inheritance by the target web's *other* lists is
  not reproduced; create those out of band (CSOM/PnP).

  What is left is reported rather than left silent: the resolver compares the two
  webs *after* provisioning (`compare_web_scope_structure`) and appends what the
  target web still lacks — `web-scope structure is incomplete: the target of <url>
  lacks 1 content type(s): Contract — …`. That comparison is read-only (two
  projected GETs per web), matches columns by internal name and content types by
  name, and ignores hidden, system, framework and sealed columns, so a note names
  real gaps rather than platform plumbing. It counts *definitions*, not user
  intent: a site collection root also carries app- and feature-provisioned site
  columns (compliance, taxonomy, community, tenant "modern" UI columns), so a long
  list means "the target web is not a schema clone of the source web", not
  "recreate N columns".

- **Field links are replayed in batches, and read back to decide the warnings.**
  All content types of a list are reconciled together: their links are read in one
  `$batch`, the missing ones are added in a second, and the links are read again
  after the write. That round of three requests replaces the one-per-link
  exchange, which was the bulk of a structure replay (~35 requests for a
  ten-column, five-view list; ~60 % of them field links). The read-back is not
  redundant: the adds travel in a change set, which SharePoint applies atomically,
  so one refused column rolls back its siblings while their sub-responses still
  answer `200` — the re-read is what lets `warnings` name every column that is
  *not* linked, with the server's reason attached to the column that caused it.
  Link **order** is restored per content type, only when the read-back shows the
  server kept a different order, so a column the server refused is never sent in a
  `Reorder` array and a re-run over an already-correct list writes nothing.

A structure-provisioning warning is also recorded on the resolved target adapter,
so a whole-site session reports it through `session.warnings()` instead of only in
the log.

### List container settings

The snapshot also carries the list's own policy — `EnableVersioning`,
`MajorVersionLimit`, `EnableModeration`, `DraftVersionVisibility`,
`EnableAttachments`, `ReadSecurity`, `WriteSecurity`, `ValidationFormula` /
`ValidationMessage`, plus `EnableMinorVersions`,
`MajorWithMinorVersionsLimit` and `ForceCheckout` on a document library — and
provisioning replays it as per-property `MERGE` requests — the differing ones
together in one `$batch`. Four details are worth knowing, all live-verified:

- **Only differing settings are written.** The target's current values are read
  first (one `GET`), so a list created from the same template — which already
  carries most of them — is left alone and a re-run writes nothing. This is not
  only an optimisation: SharePoint rejects some writes whose value is *already*
  correct (a version limit while versioning is off, a system library that grants
  no write), which would otherwise surface as warnings about settings that match.
- **Settings are applied regardless of `on_conflict`.** The snapshot *is* the
  wanted policy, and the item copy depends on it: an item's approval status only
  exists on a list that enables moderation, so enabling it after the items landed
  would be too late.
- **Order matters.** Versioning is applied before its limits, versioning and
  moderation before the draft-visibility policy, and validation **after** the
  columns exist (its formula names them). A version limit whose versioning flag is
  off in the snapshot is not sent at all — the server rejects it outright
  (`Versioning must be enabled and the number of major versions must be between 1
  and 50000`).
- **A setting the list cannot accept is a warning, not a failure.** A plain list
  rejects minor versions, their limit and required check-out (`The list does not
  support minor versioning.`), which is why those three are captured and applied
  only for a document library. The differing settings go out in **one** `$batch`
  rather than one request each; because a change set is atomic, a refusal makes
  the whole write fall back to sending them one by one through their own handles,
  so one rejection still cannot leak into the next and cannot leave a
  half-configured list behind a `200` per survivor.

The server canonicalizes a validation formula (`=IF([Title]="",FALSE,TRUE)` reads
back as `=IF(Title="",FALSE,TRUE)`), so `verify_list_structure` compares it with
whitespace and brackets stripped and reports any other difference as a
`settings_mismatch`.

### Site settings

Replaying a list's structure reproduces its columns, content types, views and
container settings — never the web that hosts them, so without this a migrated
site would keep the *target* web's identity where people actually read it (site
header, site card, search results). The web-scope settings that are plain writable
strings over REST are copied (one projected GET per side, then a single MERGE):

- `Title`
- `Description`

Only **differing** values are written, so the copy is idempotent and a re-run does
not bump the target web's metadata; an unset source value clears the target's
(these properties reject `null`). Copy is on by default
(`MigrationSettings.migrate_site_settings="PRESERVE_ALL_SETTINGS"`, or
`--no-site-settings` in the example); `"NONE"` leaves the target web alone, and any
other value raises rather than silently doing nothing.

```python
from office365.migration.sharepoint import apply_web_settings, verify_web_settings

apply_web_settings(source_web, target_web)  # -> WebSettingsReport(applied={"Title": "team"})
verify_web_settings(source_web, target_web)  # -> [] once the copy landed
```

The site-settings surface is **live-verified** on SharePoint Online: the copy wrote
only the property that differed, a second run wrote nothing, `verify_web_settings`
was clean afterwards and reported the drift again once the target was restored, and
a subsite was copied the same way (including clearing a `Description` back to the
source's empty one).

What a web-settings copy leaves behind, by design:

- **Branding** — master page, theme, `SiteLogoUrl`, alternate CSS. Carried by its
  own module with its own rules: see [Site branding](#site-branding).
- **Site-collection and regional settings** — time zone, locale, quotas, sharing
  capability, hub association. REST exposes no working write path (setting a
  `TimeZone` id does not change the web's zone), so they are neither copied nor
  attempted; the `site_settings` fidelity dimension carries that note.

Each web is copied through **its own** context, so with `include_subwebs=True` a
mirrored subsite also gets the source subsite's title and description.

### Site branding

Copying content and replaying structure still left the *web* looking like the
target: its own master page, its own theme, no site logo — the first thing a user
sees. `office365.migration.sharepoint.branding` carries the properties REST
accepts (`MasterUrl`, `CustomMasterUrl`, `SiteLogoUrl`, `AlternateCssUrl`,
`ThemedCssFolderUrl`) through `apply_web_branding(source_web, target_web)`: one
projected GET per side, then a single MERGE of only the properties that differ, so
a re-run is a no-op. `verify_web_branding(source_web, target_web)` is the
read-only half (one finding per property), and `verify_site(...)` reports it as its
own `branding` dimension next to `settings`.

Three rules make a blind copy wrong, and each is enforced rather than assumed:

- every value is a path **inside the source site**, so it is rebased onto the
  target's before it is written — copying it verbatim would leave the migrated web
  pointing back at the site it came from (`/sites/team_in/…` → `/sites/team_out/…`,
  including when the value is an absolute URL). Master pages read back as
  *site-relative* paths on every web, so without the rebase every migrated site
  would report a master-page mismatch;
- every one of them names an **asset**, so a value is written only where the
  target resolves it. A master page or theme folder lives in a gallery this
  migration never copies (`_catalogs/masterpage` and `_catalogs/theme` are hidden
  lists); a logo may be the site's group image
  (`/sites/x/_api/GroupService/GetGroupImage?id=…`), a service endpoint with no
  counterpart to copy. In both cases the web keeps its own value and the run
  reports `branding: … keeps its own MasterUrl — the target has no …`: a dangling
  master page would break every page on the site, so this is a reported gap rather
  than a hopeful write. An absolute URL is resolved to its path for that check;
- only the logo and the alternate CSS can be **cleared** — an unset source value
  writes `""`, which the service accepts and which a second run leaves alone. A
  blank master page is never written.

Branding is applied **after** the content, because an alternate-CSS URL may point
into a library this run has just populated. Live-verified on SharePoint Online: a
MERGE of `SiteLogoUrl` + `AlternateCssUrl` on a web is accepted and reads back,
writing `null` clears the logo, `MasterUrl` reads back as a site-relative path,
and a source web's alternate CSS arrived rebased on the target with `verify_site`
reporting `branding: 0`.

### Site pages

A *Site Pages* library (`base_template` 119) holds `.aspx` pages rather than
documents, so the item adapters do not migrate it. Both kinds of page it holds are
reachable over REST, so the whole-site resolver copies them
(`resolve_site_task(..., migrate_pages=True)`, the default):

1. read the source page library once, projecting `Id, FileLeafRef, Title,
   Description, ContentTypeId, CanvasContent1, LayoutWebpartsContent, WikiField,
   PromotedState, BannerImageUrl, OData__ModerationStatus`;
2. classify each page — **modern** when its content type id starts with
   `0x0101009D1CB255DA76424F860D91F20E6C4118` (or it serializes a canvas),
   **classic wiki** when only `WikiField` has content, and *uncopyable* when it
   has neither;
3. create the target page — a modern page through `POST /_api/sitepages/pages`
   (`Web.add_site_page(name, title=...)`), a wiki page through
   `List.create_wiki_page(name, body)` — and read the new id back (`Id`; the
   modern create response carries no `Name`);
4. write the page content onto the created item: for a modern page a MERGE of
   `Title`, `Description`, `CanvasContent1`, `LayoutWebpartsContent`,
   `BannerImageUrl`, `PromotedState` (only the values the source actually carries,
   and an *empty* canvas is left alone because a new page already ships a default
   one); for a wiki page the source `WikiField` body plus `Title`/`Description`;
5. publish it when the source page was published — for a modern page
   `POST /_api/sitepages/pages(<id>)/publish`, for a wiki page
   `item.file.publish(comment)` — then read the body back once to confirm it
   landed;
6. point the target web's **home page** at the copy of the source's
   (`apply_home_page`, called at the end of `copy_site_pages`): the source's
   `WelcomePage` is resolved through the copy's renames — a page copied as
   `Home-1.aspx` becomes the home page — and written onto the target's *root
   folder* only when it differs. A source home page that was not copied is
   reported, not guessed at, and the target keeps its own.

Four server facts this relies on are **live-verified** on SharePoint Online: a
page created that way is a *draft* until the publish operation runs (a MERGE of
`OData__ModerationStatus` does **not** publish either kind of page), a page's
`CanvasContent1` round-trips byte-identical through an item MERGE (the source
canvas is stored already entity-encoded, so no normalization is needed), a
`WikiField` body does too — the server normalizes a body once on create (it wraps
it in an `ExternalClass` div and entity-encodes braces), so a copy reuses the
*source* value verbatim instead of re-authoring the body — and a web's
`WelcomePage` is **not** writable through the web: a MERGE of it on `/_api/web`
returns success and changes nothing, while the same MERGE on `/_api/web/rootfolder`
moves the home page. That trap is why `apply_home_page` writes the root folder
(`Web.root_folder`) rather than `Web.set_property("WelcomePage", ...)`.

Copies are **add-only** — an existing target page is never deleted. The duplicate
behaviour is explicit, using the SPMT vocabulary
(`MigrationSettings.duplicate_page_behavior`, or `--duplicate-pages` in the
example): `RENAME` (default: `Home.aspx` → `Home-1.aspx`, never reusing a taken
name), `SKIP` (leave the target page as it is) or `OVERWRITE` (MERGE onto the
existing page). `verify_page_copy(source_web, target_web)` reconciles the result
read-only: a source page counts as delivered when the target has the same name or
an identical canvas, anything else is reported as `missing` or `drifted`, and a
target whose home page is not the copy of the source's is named as such.

The copy is **idempotent**: a page's body is its identity (a copy writes the
source body verbatim and publishes it), so a second run over the same source and
target finds its own earlier copy — including the one it renamed around an
existing page — and leaves it alone instead of minting `Home-2.aspx`,
`Home-3.aspx`, … on every run. Such pages are listed in
`PageCopyReport.unchanged`, and the home page designation follows them, so a
re-run keeps the site opening on the copy. `OVERWRITE` and `SKIP` are unaffected;
each target page accounts for at most one source page, so two source pages with
an identical body stay two copies.

What a copy still cannot do, stated plainly:

- **Publishing pages**, and pages with neither a canvas nor a wiki body, are
  transformation work, not copy work. They stay a handoff:
  `detect_page_handoff` inventories them, and
  `page_handoff_note(handoff, modern_copied=True)` names only the ones that were
  *not* copied. A copied page is listed in `PageCopyReport.copied`, with the
  classic ones also in `PageCopyReport.wiki`.
- A **client-side web part** serializes the source list/library identifiers it
  binds to; those are not remapped, so a copied page can render a web part pointed
  at the source. The note reports the web-part count per page. A classic wiki
  body is copied **verbatim**, so wiki markup that hard-codes the source site —
  internal links, wiki-embedded web parts — still addresses the source site; the
  copy warns per page rather than rewriting the markup.
- **Version history** of a page is not restored (REST cannot write it), and a
  target page that is *checked out* by someone else cannot be created or
  overwritten — the create fails with SharePoint's own check-out error and the
  page is listed under `PageCopyReport.failed` rather than aborting the run.

These points were exercised live: a run over a source web with three pages copied
two — one modern page renamed around an existing target page, and one classic wiki
page whose `WikiField` body (162 characters, braces and an internal link included)
read back byte-identical and published to `1.0` — and reported the third as failed
because its target name was held by another user's check-out. That same run left
the target's own home page alone and said so, because the source's home page
(`SitePages/CollabHome.aspx`) was the page the check-out blocked; a second run
with a copyable home page moved the target web's `WelcomePage` onto the copy and
`verify_site` confirmed it.

## Monitoring a run

A session is long and headless: without a progress hook it prints nothing between
"Migrating…" and the summary. `office365.migration.logging` supplies the two pieces
an operator needs, and nothing that ties this library to a monitoring product.

**Events.** Every boundary emits one structured event on the
`office365.migration` logger — `run.started`/`run.completed`,
`plan.started`/`plan.completed`, `job.started`/`job.completed`/`job.failed`,
`progress` — through `log_event(...)`. `JsonLogFormatter` renders each as one JSON
object per line with a stable shape, so a filter never has to parse prose:

```json
{"ts":"2026-02-11T09:12:03.114Z","level":"info","logger":"office365.migration",
 "event":"job.completed","message":"library:/sites/t/Documents: 168 copied, 2 skipped, 0 failed",
 "source":"library:/sites/s/Documents","target":"library:/sites/t/Documents",
 "phase":"completed","success":168,"skipped":2,"errors":0,"bytes_transferred":734003200,
 "duration_ms":184233}
```

There is deliberately **no per-item event**: a five-hundred-thousand item library
must not produce five-hundred-thousand lines, so items are counted and only
failures get a line of their own (`job.failed` carries the error text). Notes a
resolution step collects — a list that lost its field links, a list setting the
target refused — go to the caller's warning sink (`session.warnings()`), which is
what a console and a report read; they are also logged at `DEBUG` for provenance,
so a message is never printed twice (once by the logger, once by the caller). A
caller that ships logs rather than prints them can emit each of them as a
`run.warning` event (`count` included) — the example does, under `--log-json`.

**Progress.** `ProgressReporter` is a plain `ProgressCallback` that reduces the
runner's per-item snapshots into a throttled heartbeat with a rate and an ETA —
it drops into `session.start(progress=...)`, `job.run(...)` or any long-running
runtime operation:

```python
from office365.migration.logging import ProgressReporter, configure_json_logging

configure_json_logging()  # JSON lines on stderr
reporter = ProgressReporter(interval=15)  # one heartbeat per 15s
session.start(progress=reporter)
print(reporter.summary())  # "1,234/5,000 (24.7%) 41.2/s ETA 1m31s"
```

The window restarts when a new container (a different total) begins and when the
stage changes — a rate measured while planning says nothing about the copy that
follows it, which is what used to print an ETA of several hours on a run that was
seconds into copying. The rate stays `None` until there is at least half a second to
measure, and `close()` emits a last heartbeat only when the interval swallowed the
final count.

**Shipping the log.** Emit JSON lines and let the machine's own collector ship them:
an OpenTelemetry Collector's `filelog`/`stdout` receiver into Loki or Azure Monitor,
Promtail, a sidecar, `kubectl logs -f`. No exporter, SDK or vendor client is imported
here — a library must not choose a monitoring product for its caller. Alert on the
gaps rather than the totals: a heartbeat that stops (a stalled run), `job.failed`,
a rising error count, or a `run.completed` whose phase is not `completed`.

The example wires this up for you: `--stats 30` prints a heartbeat per active list,
`--log-json` (or `--log-json run.jsonl`) writes the events, `--log-level` filters
them.

**Throughput.** `MigrationOptions.concurrency` (default `1`) makes the runner drive
a list's writes through parallel workers, and `batch_size` (default `100`) sets how
many items a `$batch` carries and how often progress/checkpoints flush. The example
exposes both (`--concurrency 4 --batch-size 50`) and prints the measured rate per
list — `✓ [ 5/24] Documents  168 copied  1m42s  1.7 items/s  6.1 MB/s`, from the
`duration_ms` the session status carries — so a tuning change can be judged on a
number instead of a feeling. Concurrency buys the most on many small files and buys
nothing on a few large ones, where the upload session is already the bottleneck; it
also multiplies in-flight requests, so raise it against a throttling tenant with
care (the runtime retries a 429/503 with `Retry-After`, but the retries are time you
do not get back).

### Throttling as a measured number

Retrying a `429`/`503` is transparent by design, which is exactly what makes it
misleading: a run throttled on every batch reports the *throttled* rate, so
"is concurrency 8 faster than 4?" has no honest answer. `ThrottleMonitor` supplies
the denominator — it wraps a context's transport (sync and async) and counts
responses, `429`/`503`s and the `Retry-After` seconds the service asked for, without
changing retry, backoff or pacing:

```python
from office365.migration import MigrationSession, ThrottleMonitor

throttle = ThrottleMonitor().attach(target_ctx).attach(source_ctx)
session = MigrationSession(throttle=throttle).register(context=target_ctx)
statuses = session.start()

print(throttle.summary())  # "throttled 3/171 response(s) (429: 2, 503: 1), 42s of Retry-After"
print(throttle.snapshot())  # {'responses': 171, 'throttled': 3, 'retry_after_s': 42.0, 'by_status': {...}}
```

The session logs a `throttled` event (level `warning`) whenever the counter grows,
carrying the cumulative `responses`/`throttled`/`retry_after_s`/`by_status`, and adds
the same counters to `run.completed` — so a collector can chart throttling over time,
and `retry_after_s` is the additive cost throttling put on the run. Attaching is
cheap and inert: contexts cloned from a monitored one share the wrapper (the
whole-site resolver's every web included), and re-attaching replaces rather than
stacks. A monitor is the thing to add *before* changing `--concurrency`, or the
before/after numbers mean nothing.

The proactive lever is pacing rather than retrying: `RateLimiter(min_interval=...)`
puts a floor between requests across all workers of a run, so the tenant's limit is
approached instead of discovered:

```python
from office365.runtime.http.throttling import RateLimiter

RateLimiter(min_interval=0.25).bind(target_ctx)  # at most 4 requests/second, fleet-wide
```

Resume from the **checkpoint and manifest files**, never from a log: those are the
authoritative record of what has been copied, and a log is best-effort.

## Fidelity

| Flag | Client-side runner | Server-side package |
|---|---|---|
| `preserve_timestamps` | best-effort (`Created`/`Modified` on files, folders and list items) | ✓ carried per manifest object (`TimeCreated`/`TimeLastModified`) |
| `preserve_authorship` | best-effort (`Author`/`Editor` via `EnsureUser`) | best-effort — resolved PUID users only |
| `preserve_permissions` | best-effort (same-tenant ACLs: items, a list's own ACLs via `apply_site_list_security`, web permission levels/groups/role assignments) | best-effort — resolves users by PUID; groups / unresolved principals skipped |
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
  `ListItem.system_update`). This covers files, folder list items and record list
  items alike.
- **Authorship** — the client-side targets restore `Author`/`Editor` by resolving
  each source principal through `web.ensure_user` and writing a `FieldUserValue`.
  The values are resolved and cached, then written **in the same system update as
  the timestamps** (or in one final write when timestamps are not preserved): a
  separate authorship write cost a second request per item and re-approved the
  document the approval step had just restored. Principals `EnsureUser` cannot
  resolve are skipped (the verification reports the resulting mismatch); the
  server-side package emits `UserGroup.xml` ids instead.
- **Permissions** — the source reads the item's `role_assignments`; the target
  breaks inheritance and recreates them, resolving principals by login name and
  roles by name. Only items with an **unique** ACL are copied — the REST surface
  reports inherited role assignments too, and copying those would break
  inheritance on every item and duplicate the parent ACL. That flag is *not* part
  of a plain entity read, so an item loaded before its ACL changed keeps a stale
  value; the target therefore re-reads it explicitly rather than trusting the
  cached copy, which would otherwise break inheritance on an item that is already
  unique (wiping the assignments it was meant to keep). Every principal and role
  is resolved **before** anything is written, and inheritance is only broken when
  at least one assignment resolved: an item whose principals are all unresolvable
  (cross-tenant accounts, an app principal) would otherwise end up with an
  **empty** ACL — inheritance broken, nobody granted — so it is left inheriting
  and reported instead. A re-run adds only what is missing and never removes an
  assignment the source does not grant. On the server-side
  package target, `preserve_permissions=True` emits
  `DeploymentRoles`/`DeploymentRoleAssignments` for **resolved users** (matched by
  PUID; groups/unresolved principals are skipped with a warning). Both are
  **same-tenant**; cross-tenant identity mapping is not implemented.
- **Site security (web scope)** — with `preserve_permissions`, the SharePoint
  resolver also creates each web's **custom permission levels**, re-creates its
  **custom site groups** (flags + membership) and its **web-level role
  assignments**. A permission level is what an assignment *names*, so a target that
  lacks it cannot restore that grant at all: `capture_permission_levels(web)` reads
  each level's `BasePermissions` as a decimal mask (plus description and order) and
  a level the site defined itself (`RoleTypeKind` 0) is created when missing — same
  mask, same name. Two things are deliberately never written: a **built-in** level
  (every site has one; it is matched by `RoleTypeKind` as well as by name, so a
  localized target still lines up, and it is *reported* if genuinely absent rather
  than created), and an existing level whose mask **differs** — rewriting what a
  target site's "Contribute" means would silently change everyone's access, so it
  is reported and left as-is. Hidden levels ("Limited Access") are skipped: the
  service grants those itself whenever a scope is broken. The three associated groups
  (Owners/Members/Visitors) are mapped by name onto the target web's, so a renamed
  association still lines up; their *membership* is left to the Microsoft 365 group
  behind the team site and is **not** copied. Custom groups are created only when
  missing, and an assignment already present is left alone — so re-running is
  idempotent. Same-tenant, matched by login (`EnsureUser` for users, group name for
  groups); anything unresolvable is reported via `session.warnings()` and by
  `verify_site_security`, never silently dropped.
- **List security (list scope)** — a library whose permissions are *unique* (the
  source broke inheritance to restrict it) is a scope neither of the other two
  reaches: item ACLs say nothing about the container, and the web scope is the
  web. `apply_site_list_security(source_web, target_web)` replays those ACLs onto
  the target list: it breaks the target list's inheritance **once** (only if it
  still inherits), adds the source's assignments, and leaves everything else
  alone, so it is idempotent and a re-run writes nothing. It is called **after**
  the content — not by the resolver — because a freshly broken list is briefly
  unreadable to everyone but the writer, and because a list ACL is only meaningful
  once the list exists; `migrate_site.py` calls it right after the run whenever
  `--preserve-permissions` is set and prints `Permissions: N list(s) carry unique
  permissions, M applied`. `capture_list_security(list)` is the read-only half
  (`None` when a list simply inherits — which costs one extra GET, so it only runs
  inside a permissions pass). Verified live: a list that granted only the
  **Visitors** group `Read`, with inheritance broken, arrived on the target with
  exactly that assignment — `verify_list_security` clean — and the target's list
  ACLs were not the web's.

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
| Site groups / web role assignments | n/a (whole-site resolver only) | n/a | best-effort (same-tenant; custom groups + membership, associated-group membership excluded) |
| Attachments | n/a | n/a | delivered (content only; system metadata not settable) |
| Columns / content types / views / list settings | unsupported by the adapters — replay them with `provision_list_structure`; the whole-site resolver registers web-scope **site columns** first (`provision_web_scope_columns`), while a web-scope **content type** stays reported (`verify_site(..., web_scope_structure=True)`) | same | same |
| Lookup / Person / MMD values | unsupported (values copied verbatim) | unsupported (values copied verbatim) | best-effort (single- and multi-value Lookup remapped across migrated lists; Person by login; MMD carried by term id; multi-choice by value) |
| Check-out / draft / approval state | unsupported | best-effort (approval status + comments carried for files **and** list items when moderation is enabled; a draft file's `Modified` cannot be restored with it; a **checked-out** file is copied from its last checked-in version and a file on an **un-published (minor) version** is copied as its draft — both reported as warnings, since the readable version is all REST exposes) | best-effort (approval status + comments carried when the list enables moderation; check-out and in-progress draft state are not) |
| Navigation / pages / web parts | navigation and pages are web concerns, not adapter concerns: the whole-site resolver copies quick launch/top nav (`migrate_navigation`) and both kinds of page (`migrate_pages`) — a modern site page's canvas, title, description, layout, banner and promoted state, a classic wiki page's `WikiField` body — then publishes the ones the source had published; publishing pages stay a handoff, wiki markup is not rewritten, and a serialized web part keeps the source list/library ids it binds to | same | same |
| Site settings (web scope) | each web's `Title`/`Description` are copied onto the target web when they differ (`migrate_site_settings`), as is its branding (master page, logo, alternate CSS, theme folder) — rebased onto the target's path and only where the target has the asset; the site-collection/regional settings and activated features are not carried over REST, only compared and reported (`compare_site_scope`, `verify_site(..., site_scope=True)`) | same | same |
| Workflows / InfoPath forms / BCS external lists | not migrated (the resolver reports every association, InfoPath form and external list as a handoff) | same | same |
| Sharing links | unsupported (following tenant policy; not recreated per item) | same | same |

> Columns, content types, views and container settings are deliberately *not*
> carried by the item adapters: they are schema/policy, and the SharePoint resolver
> replays them over REST with `provision_list_structure` (whole-site and single-list
> resolution do this by default). The matrix reports the adapter-level truth.
> Replay is **per list**, with one web-level exception: a site column (its `Scope`
> names the web, not the list) is first registered at web scope by
> `provision_web_scope_columns`, so a list that carries it reuses that definition
> instead of a list-scoped copy; a custom content type used by the list is recreated
> on the target list. A content type that no migrated list uses is not created, and
> REST would not let a fresh site column be linked to a content type anyway
> (`Column '<name>' does not exist`) — see *Provisioning list structure*.

> Site groups and web-level role assignments are likewise **not** an adapter
> dimension: `describe_fidelity` models a source/target *pair*, whereas site
> security is a **web** concern applied by the resolver
> (`resolve_site_task(..., preserve_permissions=True)` → `apply_site_security`).
> It is therefore listed here for completeness but is not part of
> `report.dimensions`; `verify_site_security(source_web, target_web)` reconciles it.

> Navigation is also a **web** concern applied by the resolver: with
> `migrate_navigation` on (the default), `apply_navigation` copies each web's
> Quick Launch and top navigation bar additively (source links rewritten to the
> target; dynamic nodes such as *Recent* are skipped), and
> `verify_navigation(source_web, target_web)` reconciles the copyable links.
> Site pages follow the same pattern (`migrate_pages`, on by default): the
> resolver calls `copy_site_pages(source_web, target_web)` and
> `verify_page_copy(source_web, target_web)` reconciles the page bodies (canvases
> and wiki bodies). The `navigation` dimension is `best_effort` for that reason:
> navigation, modern pages and classic wiki pages are carried, **publishing** pages
> stay a handoff, wiki markup is not rewritten, and a modern page's client-side web
> parts keep the source identifiers they serialize — their data bindings are not
> remapped. The resolver makes the remaining gap visible:
> `detect_page_handoff(source_lists)` finds the page libraries and classifies each
> page, then `page_handoff_note(handoff, modern_copied=...)` appends a warning
> naming the pages that were *not* copied and the client-side web-part count, so a
> run never silently drops them (`detect_page_handoff` / `page_handoff_note` are
> also exported for reuse).

The three other handoff categories are detected the same way, by
`detect_handoff(web, lists)`:

- **Workflows** — the web's `workflow_associations` plus each visible list's
  `WorkflowAssociations` (expanded on the same projected read). A workflow
  definition, its association and its running instances are all server-side
  state; nothing about them is copyable over REST.
- **InfoPath forms** — a list whose declared new/edit/display form URL points at
  `FormServer.aspx`, carries an `XsnLocation=` parameter, or names a `.xsn`
  template. The stock platform forms (`Forms/Upload.aspx`,
  `Lists/X/NewForm.aspx`, `_layouts/15/aclinv.aspx`, the `_catalogs` pages) are
  matched out, so a normal library is never flagged. The `.xsn` template itself
  lives in the site's form templates and is not carried either.
- **BCS external lists** — a list whose `BaseTemplate` is `600`
  (`EXTERNAL_LIST_TEMPLATE`). It is a view over a BDC model, so the resolver
  skips it (it does not even create a hollow list) and reports it; a
  `BusinessData` **column** inside a migrated list is likewise skipped by the
  structure replay with its own warning — replaying its schema would create a
  column that resolves nothing on the target.

All notes are aggregated per web, sample the first five names and end with
`and N more`, and name the remediation (`remediate out of band`): the migration
reports the gap rather than pretending a copy is complete. Like site security and
navigation, these are **web** concerns applied by the resolver, so they are listed
here for completeness but are not part of `report.dimensions`.

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
Each `UserGroup.xml` user carries its PUID (`SystemId`) in its canonical 16-digit
hex form: `normalize_puid` strips a `0x` prefix or stray whitespace rather than
carrying it into an attribute the service parses as a number. Each granted level
is emitted as a `DeploymentRoles` `<Role>` with a fresh non-system id and a
decimal `PermMask`, and is matched by `Title` to the target's existing permission
level, so no duplicate is created. Groups and principals that cannot be resolved
to a PUID are skipped and reported as warnings.

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
| Content checksums | always, on a `spot_checks` sample | `mismatches` (or `unverifiable` if a side exposes no comparable hash); a checked-out source file's pending edits, and the published version an un-published draft supersedes, are invisible to both sides and are reported by the source instead |
| Timestamps (`Created`/`Modified`) | when `preserve_timestamps` was requested | `mismatches` / `unverifiable` (attachments: content-only, reported once; folders: compared on the folder resource, applied last) |
| Authorship (`Author`/`Editor`) | when `preserve_authorship` was requested | `mismatches` / `unverifiable` |
| Permissions | when `preserve_permissions` was requested | `mismatches` / `unverifiable` |
| Versions | when `preserve_versions` was requested | always `unverifiable` over REST |

For SharePoint list items the source and target are paired by the
`MigrationSourceId` marker (see [Migrating list items](#migrating-list-items));
attachment presence *and* content (md5) are checked, and each record's scalar
content columns are hashed on both sides, so a field-value difference is a real
`mismatch` rather than an `unverifiable` caveat.

Record timestamps and authorship are written as a **system update** — CSOM
`ListItem.UpdateOverwriteVersion`, exposed over REST as
`ValidateUpdateListItem(..., bNewDocumentUpdate=True)`. That writes
`Created`/`Modified`/`Author`/`Editor` *without* creating a new version, so a
migrated record keeps the single version it arrived with instead of gaining one
version per fidelity write. (Passing `bNewDocumentUpdate=False` would create a
new version for every write.) Both property groups travel in that **one** call —
authorship is resolved first and folded in, rather than paying a system update of
its own that the timestamp write would then repeat. Because SharePoint has no client-side path to set
an attachment's own system metadata (an attachment has no backing list item),
attachments are migrated **content-only**: they are presence- and md5-checked, and
the timestamp/authorship/permission diffs exclude them with a single
`unverifiable` note rather than one caveat per attachment.

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
print(report.summary())  # "MISMATCH | Projects | columns: 2, content types: 1, views: 0, field links: 1, ..."
if not report.ok:
    print(report.to_dict())
```

Only *missing* structure is reported: a freshly created target list legitimately
carries extra built-in columns, content types and views, so "extra" entries are
not findings. Field links that could not be attached (the REST limit described
above) show up as `missing_field_links`.

That comparison is limited to the columns the migration can **recreate**. A content
type's links also name built-in and SharePoint-owned columns — `Title`,
`FileLeafRef`, and the framework columns SharePoint provisions for itself
(`MediaServiceMetadata`, `MetaInfo`, `_VirusStatus`, …) — which are hidden or
non-deletable and therefore neither copied nor linked: linking one is a guaranteed
server error. Those names are dropped at capture time (and logged at debug level),
so a library like *Site Assets* reports `field links: 0` instead of a permanent
handful of links to columns no migration was ever going to create.

A column that both lists have is compared **attribute by attribute**, not just by
name: the type, `Required`/`Indexed`/`EnforceUniqueValues` flags, length, format,
rich text, the choice list, the default value, a calculated or validation formula
and its message, and a calculated column's field references are read out of each
`SchemaXml` and must match, otherwise the difference lands in `column_mismatches`.
Only attributes that describe the *containing* site or are assigned by the server
are ignored — the owning list id, a lookup's target list, a taxonomy column's
hidden note list, the column id and its storage column/ordinal — because a faithful
re-create legitimately changes those. A formula is compared with brackets and
whitespace stripped, the form its own read-back takes.

### Verifying site settings

A copied web title is a one-line check (read-only, two projected GETs):

```python
from office365.migration.sharepoint import verify_web_settings

for note in verify_web_settings(source_web, target_web):
    print(note)  # "site settings: …/sites/team_out Title is 'team_out', source has 'team'"
```

Branding is checked the same way — `verify_web_branding(source_web, target_web)` —
comparing the source's paths *rebased* onto the target site, so a master page that
moved from `/sites/team_in/…` to `/sites/team_out/…` is not reported as drift while
a property that genuinely differs still is.

The example's post-run reconciliation calls it for every migrated web, so a run
whose settings copy silently failed (an app principal without web write access,
for instance) shows the difference instead of reading as a clean pass. Anything a
copy cannot carry — a master page or theme the target lacks, site-collection and
regional settings — is named by
the `site_settings` fidelity dimension rather than reported as drift.

### Verifying site scope

Two site-level facts decide what the target site *can do*, and a migration replays
neither. They are compared rather than assumed:

```python
from office365.migration.sharepoint import compare_site_scope, site_scope_note

diff = compare_site_scope(source_ctx, target_ctx)  # read-only, both sides
print(site_scope_note(diff, "https://…/sites/team_in"))  # None when nothing is missing
```

`compare_site_scope` reads the features activated on **the web** and on **the site
collection**, plus the comparable regional settings (time zone, `LocaleId`, work
days, first day and week of the year, calendar, `AdjustHijriDays`, date/time
separators, `Time24`, `DateFormat`). Only what the *source* has and the target
lacks is a finding: a feature the target activated on its own is carried in
`to_dict()` under `extra_web_features` / `extra_site_features`, but it is not a
fidelity loss and never turns the report into a mismatch.

Neither is repaired, for two different reasons. Activating a feature has side
effects the source never asked for at this point in a run — a publishing feature
installs page layouts and swaps the master page — and deactivating one is not
something a re-run undoes, so it stays an explicit out-of-band decision:
`Enable-SPFeature` with the GUID the note prints. Regional settings have no working
REST write path (setting a time zone id does not change the web's zone), which is
also why the settings copy never attempts them.

`verify_site(..., site_scope=True)` runs this as the `site scope` dimension, next
to `branding`, and it is on by default — a run that is silent about features is
reporting that the target has all of the source's, not that nobody looked.

Both paths were exercised against a live tenant: a migrated pair reports
`site scope: 0`, and two unrelated sites report 22 missing web features and 34
missing site-collection ones. A *regional* difference is only unit-tested — a tenant
cannot be talked into one over REST, which is the whole reason it is reported.

### Verifying site pages

Pages are not files with a hash, so the check compares the artifact that carries
the content — the canvas of a modern page, the `WikiField` body of a classic one:

```python
from office365.migration.sharepoint import verify_page_copy

notes = verify_page_copy(source_web, target_web)  # read-only
for note in notes:
    print(note)  # "1 page(s) have no target counterpart: CollabHome.aspx"
```

A source page counts as delivered when the target has a page of the same name
**or** a page whose canvas is identical — so a deliberately renamed duplicate
(`Home-1.aspx`) is not reported as drift. Everything else lands in one of two
findings: pages with no counterpart, and pages whose canvas differs from the
source's. Classic pages are not compared at all; they are handoff, and
`page_handoff_note` names them.

### Verifying a whole site

A whole-site run touches a web on several axes, and each has its own verifier.
`verify_site` folds them into one report with one verdict — so "did this web
migrate?" is a value, not a reading exercise:

```python
from office365.migration.sharepoint import verify_site

report = verify_site(
    source_ctx,
    target_ctx,
    pages=True,
    security=True,
)
print(report.summary())  # "MISMATCH | … | settings: 0, branding: 0, web-scope structure: 0, site scope: 0, pages: 1"
print(report.ok, report.complete)
for note in report.issues:
    print(note)
```

The checks are opt-in, matching what a run claimed to do: `settings`, `branding`,
`web_scope_structure` and `site_scope` are on by default (they report what a run
did **not** deliver, so silence has to be earned), `navigation`, `pages` and
`security` are passed when the corresponding run flags were set, and
`lists=[(source, target), …]`
adds per-list structure reconciliation (the same comparison as
`verify_list_structure`). `security=True` covers both container scopes as two
separate dimensions — `security` (web groups + web role assignments, via
`verify_site_security`) and `list security` (each list's own ACLs, via
`verify_list_security`) — because a list can be restricted while the web is fine,
and the two are fixed by different passes. Everything is read-only.

Two verdicts, deliberately separate: `ok` is False as soon as any check
contradicts the target, while `complete` is False when a check *could not run*
(access denied on a site groups read, for instance) — a partial verification never
reads as a pass. `to_dict()` is the JSON-serializable form for an evidence pack,
and the example's post-run reconciliation prints exactly this report.

## See also

- [Data pipeline](data-pipeline.md) — tabular import/export
- [Large lists](large-lists.md) — thresholds that shape a migration plan
- [Limits](limits.md) — the service limits the toolkit respects
