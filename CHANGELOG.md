# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/),
and this project adheres to [Semantic Versioning](https://semver.org/).

## [Unreleased]

Two stories: the SharePoint migration layer grew from "copy items" to a resumable,
verifiable site copy, and the runtime grew async/await, long-running operations and
a set of write/lookup primitives that the generated surface lacked.

### Added

**SharePoint migration**

- **Whole-site (same-tenant) migration.** `MigrationSession.add_site_task(...)`
  resolves a `migrate_all` task into one job per list — each with its own manifest
  and checkpoint — creating missing target containers and replaying each list's
  structure (columns, content types, views, container settings) before content is
  copied. `include_subwebs=True` mirrors the source subsite tree.
- **Several lists at once, and both phases reported.**
  `MigrationSession.start(concurrency=N)` runs `N` list jobs in parallel, each on a
  `ClientContext` clone that shares the auth context, transport and `RateLimiter`
  (adapters are re-addressed with `rebind()`, since a context owns one
  pending-query queue); `add_site_task(progress=...)` heartbeats the resolution
  phase (`lists`, `containers`, `structure`, then `pages`/`navigation`/`branding`)
  instead of staying silent. Example flag: `--lists-in-flight N`.
- **Throttling as a measured number.** `ThrottleMonitor` counts responses,
  `429`/`503`s and the `Retry-After` seconds a run waited for (observation only:
  retry, backoff and pacing are untouched); `MigrationSession(throttle=...)` logs
  `throttled` events and adds the totals to `run.completed`. Example flag:
  `--pace SECONDS`, the proactive lever.
- **Web scope, not only lists.** Branding (master page, theme, logo, rebased asset
  URLs), `Title`/`Description`, custom permission levels, web role assignments,
  Quick Launch and top navigation, the home-page designation, and modern site
  pages plus classic wiki pages are copied. Workflows, InfoPath forms, BCS
  external lists, checked-out files and un-published (minor) versions cannot be
  produced by a client-side copy, so each is reported instead.
- **Site-scope honesty.** The features (publishing, records management, document
  id) and regional settings a copy never replays are compared and reported, and
  one verification report answers "did this web migrate?" across content,
  structure, settings, pages and security.
- **Structure fidelity.** Column and view formatting JSON, taxonomy
  (`TaxonomyFieldType`/`…Multi`) values, multi-choice, hyperlink, multi-value
  lookup and person remapping, a content-type identity map (SharePoint assigns
  recreated types fresh ids), folder item metadata, list container settings with
  approval state, and attribute-level column verification (`Required`, `Indexed`,
  choices, validation).
- **Delta re-runs name the drift** a copy cannot reconcile: a source deletion
  leaves a target orphan, a rename or move looks like a new item.
- **Record-list fidelity hooks** (timestamps, authorship, unique permissions),
  matching what the document-library adapters already did.

**Runtime**

- **Async/await across the query API:** `execute_query_async`,
  `execute_query_async_retry`, `execute_query_parallel_async` (with an `on_error`
  collector), `execute_batch_async`, `get_all_async`, `export_to_async`,
  `retry_async`, async `beforeExecute`, `RateLimiter.acquire_async`/`paced_async`,
  an abort path that cancels in-flight siblings, `contextvars` preserved across the
  offloaded call, a tunable offload pool, and an optional native-async
  `HttpxTransport` (`[httpx]` extra).
- **Streaming and large data:** `BaseTransport.stream`/`stream_async`,
  `File.download_session`/`download_session_async` and `DriveItem` content streams,
  `DriveItem.resumable_upload_async`, bounded-memory `export_to`, high-level
  `Folder.download` / `FileCollection.download`.
- **Long-running operations (LRO):** a transport-agnostic `OperationPoller`
  (Operation-Location / Azure-AsyncOperation / `Retry-After`, terminal states,
  continuation tokens, cancel + timeout + progress hook), the `PollableOperation`
  mixin, `LongRunningOperationResult`, `Prefer: respond-async` helpers,
  `TeamsAsyncOperation.poll_for_status_async`, streamed report export, and
  awaitable `MigrationServerJob.monitor_async`/`progress_async`/`errors_async`.
- **Write primitives:** a unified `EntityCollection.upsert` (idempotent
  create-or-reconcile), `EntityCollection.update_all`, `Entity.update_properties`,
  `Entity.delete_object(ignore_missing=True)`, `List.ensure_field`/`ensure_fields`,
  `Field.schema_xml_for_copy()`, batch `$batch` writes, and token-aware
  `Web.get_securable_object`.
- **Lookups:** one rule for `get_by_*` (resolve one) versus `find_by_*` (return
  `None`), tolerant Graph resolvers, `ClientObject.get_or_none()`, and a bounded
  `single()`.
- **Query capabilities:** declarative `@query_capabilities(...)` with
  property-level `Prefer` injection, and a
  `Prefer: include-unknown-enum-members` helper.
- **Auth and identity:** `ClientRuntimeContext.with_auto_retry(...)` (inherited by
  clones), a typed `AccessDeniedException` for 401/403, `@require_permission`
  hints on denied requests, `Credential.is_expired`/`days_until_expiry`/
  `expiry_status`, idempotent `Application.ensure_certificate`,
  `with_certificate(public_certificate=...)` without a thumbprint, idempotent app +
  service-principal setup and application-permission grants, async token
  callbacks, and `Sites.Selected` helpers (`Site.grant_access`).
- **Smaller surface:** `client.domains` as a `DomainCollection`,
  `RestorePointCollection` with a typed `search`, `PlannerTask.assign_to` plus
  checklists, `NotebookCollection.ensure`, OneNote pages from in-memory HTML,
  `ReportResult.to_text()`/`csv_rows()`, `AttachmentBase.content_bytes`,
  readable `__str__`/`__repr__` for runtime objects, and term-store hierarchy
  export/import without the payload name clash.

### Changed

- `verify()` reports unexpected target items as such (a new
  `VerificationReport` field) instead of as content mismatches.
- Planner writes derive from `PlannerEntity`: `If-Match` from the latest etag plus
  `Prefer: return=representation`, so consecutive updates no longer fail with a
  stale-token `409`.
- Report calls return `ReportResult` (was `ClientResult[bytes]`), the Security API
  lives at `office365.security`, `TaskStatus` moved to
  `office365.todo.tasks.taskstatus`, twelve duplicate model modules re-export the
  canonical class, and `ViewCollection.create`/`ensure_view` annotate `view_type`
  as `int | str`.

### Fixed

**Migration (client-side)**

- Item values: hyperlink columns, multi-choice columns, multi-value
  `Lookup`/`Person` (including the `Type="Lookup" Mult="TRUE"` spelling),
  taxonomy, and `ListItem.set_property` on multi-person columns are all migrated;
  bulk creates adopt the list's entity-type annotation; an empty multi-value
  column no longer fails verification.
- Item ACLs: an empty ACL, a double inheritance break and a false mismatch are
  handled; fidelity writes are applied in order (permissions, authorship,
  timestamps) and folded into one system update, so they no longer create
  versions and the exact instant is restored on both list and document items.
- Record lists: content is verified instead of reported `unverifiable`, writes
  flush and checkpoint per chunk, and `conflict_resolution=OVERWRITE` now reaches
  record targets.
- Document libraries: folders are created as folders (they were uploaded as
  files), SharePoint's own `Forms/` scaffolding and the auto-provisioned
  `SiteAssets/<web title> Notebook` are skipped rather than reported as extra
  items, folder system metadata and column values are written, approval state is
  carried, and Office Open XML documents are no longer flagged as content
  mismatches (SharePoint re-serializes them, so byte equality is unattainable).
- Structure: content-type field links skip built-in and SharePoint-owned columns,
  a nameless content type no longer sends a null name, `ContentType.set_default`
  works, `reorder_fields` sends a plain JSON array, `FieldLink.field_internal_name`
  falls back to `Name`, `ContentTypeId` declares the right OData type, V3 enums
  serialize as `Edm.Int32`, and the taxonomy `TextField` round-trips.
- Site: a re-run no longer mints `Home-2.aspx`/`Home-3.aspx`, `ClientContext.clone(url)`
  no longer sends requests to the original site, a `select` projection no longer
  drops every item value and attachment, manifest/checkpoint saves create their
  directory and are crash-safe, a stale error handler no longer swallows later
  failures, and structure-provisioning warnings reach `session.warnings()`.

**Migration (server-side package path)**

- Authors and ACLs take effect (`PermissionEntry` carries the system id, display
  name, e-mail and role masks; `MigrationItem` carries author/editor), version
  history is carried through `MigrationJob`, timestamps are emitted as valid XML
  `dateTime`, a single-list task no longer skips structure replay, `CreateFieldAsXml`
  field links are emitted, and `UserGroup.xml` writes a normalized PUID.

**Runtime and models**

- Generated Graph enums sent their CSDL ordinal instead of the wire value — the
  model now carries the member name. Two models declared the wrong OData type name,
  the generator could write into hand-written files, and a forced regeneration
  re-declared inherited dataclass fields.
- Payloads: `datetime`/`date`/`Enum`/`UUID` scalars in dict- and list-built bodies,
  reserved-word property declarations, and the concrete OData type for Teams
  members, chats (topic) and shared channels, To Do attachments and links, URL
  threat assessments, subject-rights `dataSubject`, change notifications, Intune
  role assignments, and Planner assignment/checklist maps.
- Transports and batching: a thread-safe default `RequestsTransport`,
  transport-level TLS verification and proxies, `httpx` per-request `NO_TIMEOUT`,
  batch GETs placed outside the change set, multi-phase SharePoint batch writes,
  and list-item creates deferred until the entity type is known.
- Small ones: `ReportResult` raw content, `Group.created_datetime` returning `None`,
  nested OneDrive folder addressing, `ensure_folder`/`ensure_file` on a folder
  addressed by id, sharing-link expiration dates, webhook expiration format,
  `$top` sent to `directoryRoles`, sign-in timestamps as `datetime`, doubled
  apostrophes in OData literals, certificate reuse detection in the setup scripts,
  naive credential timestamps, `has_application_permissions` false negatives,
  agreement-file inheritance, the device-flow prompt, chat members right after
  creation, and `examples/onedrive/termstore/export_tree.py`.

### Deprecated

- The collection-resolving `get_by_name` / `get_by_title` / `get_by_path` helpers
  emit a `FutureWarning`; `get_by_*` now means "resolve one", `find_by_*` means
  "return `None`". Removal in v4.

### Removed

- `SubjectRightsRequestIdentity`, the unused `MigrationMode` enum, and three stale
  duplicate model modules.

### Documentation

- New guides: `docs/migration.md` (plan → copy → verify, with the limits stated),
  `docs/async.md`, `docs/long-running-operations.md`, and an async section in the
  README and the docs reading path.
- The example galleries are now lifecycle- or resource-guided tours around a
  `quickstart.py` each: SharePoint getting-started, Teams, usage reports, Microsoft
  To Do, Intune (with a lifecycle diagram) and Purview, plus an async example
  catalog.

### Internal

- Developer onboarding reworked: credentials flow through `tests/settings.py` and
  `.env`, `python -m tests.setup` guides the setup, `tests/doctor --require` checks
  a run's prerequisites, `applications/rotate_cert.py --generate` mints a
  self-signed certificate, and `OFFICE365_USERNAME` / `OFFICE365_USERNAME_ALT`
  replace the two-user test model.
- `--log-level DEBUG` in the migration example now prints the run's events as
  plain lines (`configure_text_logging()`), instead of being a no-op without
  `--log-json`.

## [3.2.0] - 2026-09-27

### Added
- **Locked-file handling (HTTP 423):** typed `FileLockedException` (also
  `SPFileLockedException`) parses the lock holder into `.lock_owner` with remediation
  in `.GUIDANCE`; `retry_on(FileLockedException)` opts into retrying lock errors, and
  `delete_object(bypass_shared_lock=True)` sends `Prefer: bypass-shared-lock` on
  Graph and SharePoint. See `examples/sharepoint/files/handle_locked_file.py`.
- **Idempotent file provisioning:** `DriveItem.ensure_file(path, content,
  on_conflict=...)` reuses or overwrites the leaf file, creating missing parents.
- **Typed CAML query builder:** `Caml` / `CamlQuery.builder()` build `ViewXml` from
  composable expressions (comparisons, field-typed helpers, `Caml.now`, logical joins
  rendering binary-nested CAML, `where/order_by/group_by/row_limit/scope/view_fields`);
  raw `ViewXml`/`parse` remain. New modules under
  `office365/sharepoint/listitems/caml/`.
- `ImportResult` — a deferred, source-agnostic streaming import driver with a
  sequential, batch, or iterated terminal; `ClientObjectCollection.import_records()`
  and `List.from_dataframe()`.
- **Idempotent list imports:** `List.import_dataframe(..., key=..., key_field=...,
  on_conflict="skip"|"upsert")` derives SHA-256 keys and skips/updates existing rows
  (`ImportStats.skipped`, `enforce_unique`, `dry_run`).
- **Resumable imports:** `ImportResult(checkpoint=...)` persists the committed cursor
  per chunk; `resumed_from`/`checkpoint`/`ImportStats.resumed_from` expose the offset;
  `on_error="collect"` records a failing chunk and continues.
- `ClientObjectCollection.clear()` and a `concurrency` argument on
  `Entity.execute_batch()`.
- `OperationStats` shared counter base, specialized by `ImportStats`/`MigrationStats`.
- **Live import progress:** `progress` fires immediately (with the resumed offset),
  per committed chunk, and per completed batch; `run_parallel` reports on the calling
  thread; `execute_batch`'s `success_callback` fires per batch in sequential mode;
  `List.import_from(..., total=...)`.
- **Best-effort migration fidelity:** `preserve_timestamps`/`preserve_permissions`
  applied client-side via `DataSource.read_permissions`, `DataTarget.apply_timestamps`
  and `apply_permissions(item, permissions)` (`PermissionEntry`).
- **Migration guide:** `docs/migration.md`.
- **Server-side migration (full fidelity):** `Site.provision_migration_containers`,
  `provision_migration_queue`, `create_migration_job_encrypted`, and
  `get_migration_job_progress`; `MigrationServerJob.submit_encrypted`/`progress`/
  `status_fn`; `parse_progress_events`.
- **Migration API package layer** (`office365.migration.package`): models for
  `Manifest.xml`/`ExportSettings.xml`/`SystemData.xml`/`UserGroupMap.xml`,
  `PackageBuilder`, `FileSystemStaging`, `BlobStaging` (new `[azure]` extra),
  `create_staging(...)`, and `SharePointPackageTarget`. Covers the document-library
  subset; the generated XML is not yet live-verified.
- **Storage & vendor-neutrality docs:** `docs/migration.md` covers which legs need
  Azure, the `Staging` seam, and a step-by-step example.
- **Encrypted migration staging:** `BlobStaging`/`create_staging` accept an
  `encryption_key` (AES-256-CBC, unique IV); `SharePointPackageTarget` forwards it,
  and `[azure]` now also pulls in `cryptography`.
- **Migration examples:** `migrate_library_serverside.py` and the tenant-free
  `package_library.py`.
- **SPMT-style migration sessions:** `MigrationSession` mirrors the SPMT cmdlets
  (`register`/`get`/`add_task`/`remove_task`/`show`/`start`/`stop`/`unregister`), with
  `MigrationSettings`, `MigrationTask`, and a SharePoint resolver (client-side REST or
  `use_migration_api=True`); `MigrationOptions` gained `created_after`/`modified_after`.
- **`FileVersions` scan** — records files with version history, with the SMAT columns.
- **SMAT report scans:** `CheckedOutFiles`, `LargeExcelFiles`, `BrowserFileHandling`,
  `LongOneDriveUrls`, `ThicketFolder`, and `UnsupportedSiteTemplates`, sharing a
  `SiteScanRecord` base; `WebTemplateType` covers the full `Get-SpoWebTemplate`
  catalog; `Limits.LARGE_EXCEL_FILE` backs the Excel threshold.
- **Locale-independent error classification + SharePoint taxonomy:** deterministic
  `MATCH_PRIORITY` dispatch; `ClientRequestException.hresult`/`.error_type`; a
  `SharePointException` catch-all plus typed `SPFileCheckOutException`,
  `SPListDataValidationException`, `SPFieldValidationException`,
  `SPFieldValueException`, `SPDuplicateValuesFoundException`,
  `SPInvalidLookupValuesException`, `SPContentTypeReadOnlyException`, and
  `SPContentTypeSealedException`.

### Changed
- **Error classification is locale-independent:** exceptions key off the numeric
  HRESULT and/or embedded .NET type name; HTTP 423 disambiguates
  `SPFileCheckOutException` from the shared-lock `FileLockedException` (an unresolved
  423 still maps to `FileLockedException`).
- **Data-pipeline naming (breaking):** `from_*` is the streaming entry (returns
  `ImportResult`) and `queue_*` the deferred path. Removed `import_from`/
  `import_records`/`import_dataframe`/`import_from_file` and `to_json_file`/
  `from_json_file`; `FieldCollection.from_dataframe` → `ensure_from_dataframe`.
- **Architecture:** the data-interchange surface moved onto a new `RecordCollection`
  base (inherited by every typed `EntityCollection`); formats resolve through
  `runtime.converters.registry`; keyed skip/upsert is a pluggable `UpsertTarget`
  implemented by `ListItemUpsertTarget`.
- `import_from`/`import_records` gained `enforce_unique=True` and `dry_run=True`.
- `List` gained record facades (`import_from`/`import_dataframe`/`import_records`,
  `export_to`/`to_dataframe`); `List.from_dataframe` is now deferred.
- `SharePointListSource` reuses the shared record projection.
- `MigrationOptions.preserve_timestamps` defaults to `False`; unhonorable flags raise
  `NotImplementedError`; `preserve_versions` still needs the server-side Migration API.
- `Site.create_migration_ingestion_job` — `azure_queue_report_uri`/`ingestion_task_key`
  are now optional.
- **Streaming export + row-level dead-letter:** `export_to(..., page_size=...)` streams
  appendable formats; with `on_error="collect"` and a `dead_letter`, each failing row
  is dead-lettered.
- **Large-list threshold mitigations:** typed `SPQueryThrottledException`; paged
  `Folder.get_files` (refs #930/#936/#462) and `List.get_items(query, page_size=...)`;
  `List.ensure_indexed`/`Field.ensure_indexed` (the real fix for #427); a warning on
  unpaged filter/sort queries; new `docs/large-lists.md` (including #726).
- **Large-list UX:** list-view collections (`ListItemCollection`, `FileCollection`,
  `FolderCollection`) warn once at the 5,000-item threshold (refs #930/#936);
  `CamlQuery.index_candidates`/`List.index_candidates`; `List.check_query` pre-flights
  a query.
- **Migration-parity vocabulary:** `ImportResult.run(...)` aliases `execute_batch`;
  `ImportResult.verify`; a shared `VerificationReport` (`runtime.verification`).
- **More formats + path/IO parity:** `tsv`, `parquet`, `orc` and `feather`
  (`[parquet]`), `from_sql`/`to_sql` (`[sql]`), `from_duckdb`/`to_duckdb`
  (`[duckdb]`); every reader/writer accepts a path, `PathLike`, or open file.
- **DataFrame ⇄ SharePoint file bridge:** `Folder.write_dataframe`/`File.write_dataframe`,
  `Folder.read_dataframe`/`File.read_dataframe`, and `List.from_file`; codecs are
  `dataframe_to_bytes`/`dataframe_from_bytes`.
- **Typed field mapping on import:** `List.import_from(..., schema={column: FieldType})`
  coerces values into the payload shape; `coerce_field_value`; generic
  `RecordCollection.import_from(..., coerce={key: converter})`.
- **Column mapping:** `import_from(..., mapping={...})` renames source columns/keys.
- **Import verification:** `RecordCollection.verify_keys(keys)` and
  `List.verify_dataframe(df, key=...)`.
- **Dead-letter capture:** `import_from(..., dead_letter="dl.jsonl")` appends each
  collected chunk failure.
- **Import schema evolution:** `List.import_from(..., on_schema_change="evolve"|"fail")`,
  backed by an `ImportResult` `before_chunk` hook.
- **Incremental migration watermark:** `MigrationRunner` uses the persisted
  `Checkpoint.source_watermark` to skip and advance.
- Removed `office365/migration/_util.py`; helpers moved to `runtime.operations`,
  `runtime.converters.scalars`, and `runtime.converters.json_file`. Report writing is
  now per-format (`write_dataset`/`write_formats`).
- `MigrationItem` carries `created` and `author_id`/`editor_id`.
- **Idempotent metadata:** all client-side `ensure_*` share
  `runtime.queries.get_or_create.get_or_create`/`create_or_get` and accept
  `on_conflict="skip"|"update"`.
- `List.ensure_field`/`ensure_fields` and `FieldCollection.from_dataframe` now return
  the ensured entities; `List.ensure_fields_from_dataframe` was removed.
- **Breaking:** `List.from_dataframe()` returns an `ImportResult` driver; `progress`
  is keyword-only.
- The SharePoint list migration target flushes and discards each chunk.

### Fixed
- **Collection-bound OData operations are no longer generated onto item types.** A
  bindable `FunctionImport` whose `this` is `Collection(X)` was attached to item class
  `X`; the SharePoint (v3) and Graph (v4) readers now skip them, removing 49 methods
  from 24 item classes (e.g. `User.remove_by_id`, `Feature.remove`, `SubtitleFile.add`,
  `SitePublishingPage.set_multilingual`, `SiteProperties.get_lock_state_by_id`,
  `MigrationTask.batch_*`).
- **A custom session carrying its own auth handler now counts as credentials (refs #1045).**
  SharePoint requests (and the form-digest and batch paths) skip
  `AuthenticationContext.authenticate_request` when the transport carries a handler
  and nothing is configured.
- **Server-side file imports need a matching `SPListItem` (live-validated).** The
  Migration API silently skips an `SPFile` unless the package also contains its
  `SPListItem`; `PackageBuilder.add_file` now emits it. Every `<User>` must carry
  `SystemId`, and `DeploymentRoles` must not be emitted.
- **`PackageBuilder.add_role_assignment` now defaults `object_type="2"`.** The grant
  itself and `Author`/`ModifiedBy` still don't land (the target SID isn't exposed by
  the SPO REST API; parked).
- **On-prem NTLM auth works again (refs #1045).** `ClientContext(url, allow_ntlm=True)`
  delegates to `AuthenticationContext.with_credentials` and forwards
  `allow_ntlm`/`browser_mode`; the retired-SAML guard still fires for SharePoint Online.
- **`SharePointPackageTarget` no longer emits an empty `ExportSettings` `SiteUrl`.**
  It resolves the site URL or raises a clear error, and accepts a `source_type`.
- **`Manifest.xml` now matches the service shape.** It emits the library root
  `SPFolder`, the `SPDocumentLibrary`, a folder per subfolder and an `SPFile` per file;
  `UserGroupMap.xml` → `UserGroup.xml`; the `ViewFormsList` namespace is fixed.
- **Migration packages now emit the manifest files the API fetches** (`Requirements.xml`,
  `RootObjectMap.xml`, `LookupListMap.xml`, `ViewFormsList.xml`). Failed jobs are
  diagnosable via `MigrationServerJob.all_events`/`errors` and
  `SharePointPackageTarget.events`/`errors`/`diagnose`.
- **`CreateMigrationJobEncrypted` sends the AES key as base64 text** instead of
  decoding it.
- **`$skip` paging no longer collides with a server `$skiptoken`.**
- **Idempotent imports load existing keys on every run**, and `ImportCheckpoint` now
  records a source signature so a mismatch rescans the source.
- DataFrame import no longer silently drops a column colliding with a built-in field
  (it is imported with a `_` suffix and a warning).
- `series_kind`/`field_type_from_kind` handle more kinds and fall back to `Text`
  instead of raising `KeyError`.

## [3.1.1] - 2026-09-13

### Fixed
- SharePoint form digest is cached correctly again (`_valid_from` set on fetch,
  safety-margin refresh), so `/_api/contextInfo` is fetched once per site/run and
  pre-warmed before parallel `execute_batch`.
- A throttled digest refresh (`429`/`503`) is retried honoring `Retry-After`, and an
  expired/invalidated digest (`403`) is refreshed and retried once, surfaced as
  `SecurityValidationException`.
- Whole-batch throttling (`429`/`503`) honors `Retry-After` instead of exponential
  backoff.
- `File.open_binary`/`File.save_binary` no longer percent-encode the whole OData call
  ([#978](https://github.com/vgrem/office365-rest-python-client/issues/978)); only the
  path value is encoded.

## [3.1.0] - 2026-09-13

### Added
- **Migration toolkit** — product-agnostic core plus `sharepoint`, `outlook` and
  `teams`: resumable `MigrationJob`/`MigrationSession`, filesystem/SharePoint/JSON/
  Teams archive adapters, parallel transfer, a server-side ingestion job, and
  summary/item/failure reports.
- **SMAT-style pre-migration assessment** — modular scans/containers,
  `MigrationAssessor`/`MigrationTenantAssessor`/`MailboxAssessor`, typed reports
  (`LargeSites`, `LockedSites`, `MailFolders`), and CSV/JSON export.
- **Parallel execution** — `execute_batch(concurrency=N)` on `ClientContext` and
  `GraphClient`, plus `execute_query_parallel(concurrency=N)`; per-request retry
  honoring `Retry-After`.
- **Data pipeline** — CSV/JSON/NDJSON/Excel import-export, `from_csv`/`from_json`/
  `from_records`, dynamic list-item columns, and an optional pandas bridge.
- **SharePoint** — taxonomy term store (OData v2.1/V4), site primitives, folder
  download with version history, zip ↔ folder primitives, `Web.ensure_list`,
  `DriveItem.ensure_folder`, and typed field creators.
- **Generator** — OData function/action generation, a return-type descriptor/resolver,
  and list-typed primitive collection parameters.

### Changed
- Thread-safe auth and form-digest caches (single-flight refresh);
  `ClientContext.clone` shares the auth context and transport.
- First-class retry (exponential backoff + jitter) and throttling primitives;
  `ClientQuery` generics made consistent.
- Examples reorganized into product galleries and an SPMT-style migration flow
  (`assess/` → `migrate/` → `monitor/`).

### Fixed
- Long file paths in moves ([#988](https://github.com/vgrem/office365-rest-python-client/issues/988)) —
  body-based `File.move_by_path`/`MoveCopyUtil.move_file_by_path`; slashes are no
  longer percent-encoded inside OData string literals.
- Bulk OneDrive downloads ([#881](https://github.com/vgrem/office365-rest-python-client/issues/881)) —
  `download_folder` paginates children.
- SharePoint paging falls back to `$skip` with no next link
  ([#915](https://github.com/vgrem/office365-rest-python-client/issues/915)); custom
  headers are preserved across pages.
- Apostrophes in file paths ([#884](https://github.com/vgrem/office365-rest-python-client/issues/884)),
  in-memory upload streams ([#793](https://github.com/vgrem/office365-rest-python-client/issues/793)),
  and sharing-token UTF-8/padding ([#875](https://github.com/vgrem/office365-rest-python-client/issues/875)).
- `@odata.type` casting for directory collections
  ([#921](https://github.com/vgrem/office365-rest-python-client/issues/921)); principal
  path precedence ([#895](https://github.com/vgrem/office365-rest-python-client/issues/895));
  delta-token/custom query-param handling
  ([#948](https://github.com/vgrem/office365-rest-python-client/issues/948)); malformed
  JSON surfaced as `ClientRequestException`.

### Internal
- Generator metadata readers/model moved from `office365/runtime/odata` to
  `generator/odata`; generator checkpoints are no longer tracked.
- Unit suite consolidated into themed modules; pyright clean.

## [3.0.0]

### Breaking
- **Python 2 dropped** — minimum Python version is now 3.8
- **ACS/SAML retirement** — `with_user_credentials` now raises `RuntimeError` for SharePoint Online. Use `with_username_and_password` (MSAL ROPC) instead. ACS App-Only (`with_client_credentials`) marked as deprecated.
- **USGovernment GCC endpoints corrected** — were using wrong URLs
- Model surface updated across SharePoint, Graph, and security namespaces (see Removed below)

### Added
- Full type hints across all modules (runtime, directory, onedrive, outlook, teams, sharepoint, intune, and more)
- `with_username_and_password` (MSAL ROPC) for SharePoint Online auth
- Substantially expanded Graph model coverage: Defender/security evidence types, subject rights requests, retention labels, threat intelligence, and more
- Expanded Intune (Cloud PC) and Teams admin/communication model surface
- New query/example modules for SharePoint, Graph, and Entra ID scenarios

### Changed
- Modernized SharePoint models and generator with Python 3 type hints (`Self`, `X | None`)
- `datetime.utcnow()` replaced with timezone-aware alternatives (Python 3.12+ deprecation)
- Generator tooling: `entity_type_name` support, EnumType generation, template-driven model props
- Credential/guard improvements for Entra ID multi-resource (via `ResourceName`)

### Fixed
- Cryptography CVEs updated to 48.0.0
- Circular import in `client_runtime_context.py` / `read_entity.py`
- `NameError: name 'List' is not defined` in `fields/collection.py`
- `single()` and `first()` return types (never return `None`)
- `AttributeError: 'str' object has no attribute 'get'` when SharePoint returns a string error payload
- Pyright type-checking errors across the library and tests

### Removed
- Python 2.7 support
- `.travis.yml` (use GitHub Actions instead)
- `requirements.txt` / `requirements-dev.txt` (use `uv`/`pyproject.toml`)
- Deprecated/renamed model classes superseded by the regenerated schema

### Internal
- CI moved to GitHub Actions (ruff, pyright, offline pytest)
- Dependency management via `uv` and `pyproject.toml`

---

## [2.6.2]

- Support Access Token Refresh for MSAL-provided tokens ([#953](https://github.com/vgrem/office365-rest-python-client/issues/953))
- Resolved `get_comments()` method issue ([#956](https://github.com/vgrem/office365-rest-python-client/issues/956))
- Added Reply-To and HTML ItemBody type support in `send_mail` ([#958](https://github.com/vgrem/office365-rest-python-client/issues/958))
- Fixed `File.open_binary` issue ([#960](https://github.com/vgrem/office365-rest-python-client/issues/960))
- Fixed linting GitHub Action ([#961](https://github.com/vgrem/office365-rest-python-client/issues/961))

## [2.6.0]

- Support for Azure environments in `ClientContext` (USGovernment, GCC High, etc.)
- Auto-renewal of authentication cookies for `with_user_credentials` (after 30 min expiry) ([#950](https://github.com/vgrem/office365-rest-python-client/issues/950))
- Support for worksheet [used range](https://learn.microsoft.com/en-us/graph/api/worksheet-usedrange) API ([#926](https://github.com/vgrem/office365-rest-python-client/issues/926))

## [2.5.14]

- Added `include_resource_data` to `SubscriptionCollection.add` ([#900](https://github.com/vgrem/office365-rest-python-client/issues/900), [#901](https://github.com/vgrem/office365-rest-python-client/issues/901))
- Added urllib percent-encoding to URLs ([#918](https://github.com/vgrem/office365-rest-python-client/issues/918))
- Microsoft Search API enhancements

## [2.5.13]

- JSON batch request fixes ([#835](https://github.com/vgrem/office365-rest-python-client/issues/835))

## [2.5.12]

- Batch request fixes and improvements ([#788](https://github.com/vgrem/office365-rest-python-client/issues/788))

## [2.5.11]

- Fixed error creating a choice field ([#873](https://github.com/vgrem/office365-rest-python-client/issues/873))
- Fixed `shares.by_url` method ([#872](https://github.com/vgrem/office365-rest-python-client/issues/872))
- Fixed failing driveItem move operation ([#627](https://github.com/vgrem/office365-rest-python-client/issues/627))
- Bumped MSAL dependency ([#869](https://github.com/vgrem/office365-rest-python-client/issues/869))

## [2.5.10]

- Fixed path issue when addressing drive items ([#866](https://github.com/vgrem/office365-rest-python-client/issues/866))

## [2.5.9]

- `DriveItem.get_files` and `get_folders` now retrieve all items beyond default page size ([#844](https://github.com/vgrem/office365-rest-python-client/issues/844))
- Fixed `__str__` raising exception when `DecodeUrl` is `None` ([#850](https://github.com/vgrem/office365-rest-python-client/issues/850))
- Added note for Entra ID permissions when updating SP metadata fields ([#847](https://github.com/vgrem/office365-rest-python-client/issues/847))

## [2.5.8]

- SharePoint resource addressing enhancements
- Introduced methods for granting and revoking delegated & application permissions

## [2.5.7]

- Added passphrase support in `ClientContext.with_client_certificate` ([#836](https://github.com/vgrem/office365-rest-python-client/issues/836))

## [2.5.6]

- Support for folder coloring in SharePoint API ([#693](https://github.com/vgrem/office365-rest-python-client/issues/693))

## [2.5.5]

- Better Range support in OneDrive API ([#745](https://github.com/vgrem/office365-rest-python-client/issues/745))

## [2.5.4]

- SharePoint authentication support for GCC High environments ([#794](https://github.com/vgrem/office365-rest-python-client/issues/794))
- Fixed listing folders instead of files ([#802](https://github.com/vgrem/office365-rest-python-client/issues/802))
- Fixed addressing shared drive items ([#801](https://github.com/vgrem/office365-rest-python-client/issues/801))

## [2.5.3]

- Added `file_name` parameter to `File.copyto` and `File.copyto_using_path` ([#787](https://github.com/vgrem/office365-rest-python-client/issues/787))
- Fixed import error for `TypedDict` on Python 3.7 ([#781](https://github.com/vgrem/office365-rest-python-client/issues/781))
- Fixed `parent_folder` / `parent_collection` empty when retrieving file by server-relative URL ([#764](https://github.com/vgrem/office365-rest-python-client/issues/764))
- Fixed 401 on site property update ([#735](https://github.com/vgrem/office365-rest-python-client/issues/735))
- Fixed recipient instance reuse ([#791](https://github.com/vgrem/office365-rest-python-client/issues/791))

## [2.5.2]

- Fixed missing `typing_extensions` dependency on older Python ([#762](https://github.com/vgrem/office365-rest-python-client/issues/762))
- File/folder addressing methods fixes ([#764](https://github.com/vgrem/office365-rest-python-client/issues/764))
- Fixed share file with password ([#766](https://github.com/vgrem/office365-rest-python-client/issues/766))
- Fixed change token entity type name ([#767](https://github.com/vgrem/office365-rest-python-client/issues/767))
- Documentation fixes ([#768](https://github.com/vgrem/office365-rest-python-client/issues/768))
- CI/Linting improvements ([#765](https://github.com/vgrem/office365-rest-python-client/issues/765))

## [2.5.1]

- Added conditional import of `ParamSpec` from `typing_extensions` ([#757](https://github.com/vgrem/office365-rest-python-client/issues/757))

## [2.5.0]

- Introduced `GraphClient.with_client_secret` and `GraphClient.with_username_and_password`
- Fixed `Folder.copy_to_using_path` ([#740](https://github.com/vgrem/office365-rest-python-client/issues/740))
- Fixed `File.download_session` ([#748](https://github.com/vgrem/office365-rest-python-client/issues/748))
- Fixed `ResourcePath` collection ([#744](https://github.com/vgrem/office365-rest-python-client/issues/744))
- Typing improvements (mypy/pyright support) ([#746](https://github.com/vgrem/office365-rest-python-client/issues/746), [#747](https://github.com/vgrem/office365-rest-python-client/issues/747))

## [2.4.4]

- Fixed `FieldCollection.add_dependent_lookup_field` ([#723](https://github.com/vgrem/office365-rest-python-client/issues/723))
- Fixed 404 error with `Web.get_file_by_server_relative_path` ([#722](https://github.com/vgrem/office365-rest-python-client/issues/722))

## [2.4.3]

- Support for interactive auth via `ClientContext.with_interactive`
- Support for OAuth2 device code auth ([#713](https://github.com/vgrem/office365-rest-python-client/issues/713))
- Fixed bug with losing event handlers ([#682](https://github.com/vgrem/office365-rest-python-client/issues/682))

## [2.4.2]

- Fixed error when file is addressed by path ([#645](https://github.com/vgrem/office365-rest-python-client/issues/645))
- File/folder addressing now supports site-relative and web-relative URLs
- Support for long-running actions in Teams API with polling status
