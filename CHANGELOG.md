# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/),
and this project adheres to [Semantic Versioning](https://semver.org/).

## [Unreleased]

### Added
- **`Field.schema_xml_for_copy()`:** returns `schema_xml` prepared for
  `CreateFieldAsXml` on another site by stripping the origin-specific
  `SourceID` / `Version` attributes, which SharePoint otherwise rejects with a
  false *"The object has been updated by another user since it was last
  fetched"* error (while still creating the field).
- **Microsoft 365 Backup Storage lifecycle actions:** the tenant root's
  `restore_points` collection is now a `RestorePointCollection` with a typed
  `search(...)` action, and the CSDL actions that were not generated are
  hand-written: `ProtectionPolicyBase.activate`/`deactivate`,
  `RestoreSessionBase.activate`, `ProtectionUnitBase.offboard`/`cancel_offboard`,
  `ProtectionRuleBase.run`/`delete_and_unprotect`, `BrowseSessionBase.browse`
  and `ServiceApp.activate`/`deactivate`. The service is a **paid add-on**:
  without a Backup Storage license the API returns `UnknownError` / the service
  app must be registered first, so the examples degrade gracefully.
- **Report CSV parsing:** `ReportResult.to_text()` / `ReportResult.csv_rows()`
  decode a usage report and parse it into row dicts, decoding with `utf-8-sig`
  to strip the UTF-8 BOM Graph prefixes to the first header.
- **Named lookups for common collections:** `TodoTaskCollection.find_by_title`,
  `PlannerTaskCollection.find_by_title`, `PlannerBucketCollection.find_by_name`,
  `MailFolderCollection.find_by_display_name` and
  `NotebookCollection` / `OnenoteSectionCollection.find_by_display_name` look an
  item up by a natural key. Most use a server-side `$filter`; Graph ignores
  `$filter` on a plan's buckets/tasks and on `me/planner/tasks`, so the Planner
  lookups match client-side. Every lookup is
  deferred (run it with `execute_query()`) and tolerant by default — a miss
  leaves the returned object uninitialized (`is_loaded` is `False`); pass
  `required=True` to raise `NotFoundException` instead. `PlannerPlan.buckets`
  and `.tasks` now return those typed collections, so the planner lookups can be
  scoped to a plan.
- **Idempotent `ensure` helpers:** `NotebookCollection.ensure`,
  `OnenoteSectionCollection.ensure` and `MailFolderCollection.ensure` return an
  existing object by name or create it, reusing the create-first
  `create_or_get` mechanics — each of these services rejects a duplicate name,
  so a rerun is a no-op. `TodoTaskCollection.ensure` is filter-first because To
  Do task titles are not unique. All are deferred (run with `execute_query()`).
  OneNote's duplicate-name error (`20117`) is now classified as
  `DuplicatedObjectException`.
- **OneNote pages can be created from in-memory HTML:** `OnenotePageCollection.add`
  accepts the page HTML as a `str`, `bytes`/`bytearray`, or a file-like object
  (previously a named file was required), and its attachment mapping is typed as
  `Mapping[str, PageSource]`. `OnenoteSection.pages` now returns an
  `OnenotePageCollection`, so pages can be created directly from a section.

- **Planner assignments and checklists:** `PlannerTask.assign_to(user)` /
  `.unassign(user)` and `PlannerTaskDetails.add_checklist_item(...)` /
  `.set_checklist(items)`, backed by `PlannerAssignments.add/remove` and
  `PlannerChecklistItems.add/remove`. Both are Open Type maps keyed by id that
  mutate in place (the change is sent by `update()`), deserialize to typed
  values, and remove entries by sending `null`.
- **Client-level retry:** `ClientRuntimeContext.with_auto_retry(...)` — inherited
  by `GraphClient` / `SharePointClient` — makes every `execute_query` /
  `execute_query_async` on the context retry transient failures
  (HTTP 408/429/5xx or a dropped connection) with exponential backoff and
  jitter, honoring the server's `Retry-After`; permanent failures (400/401/403/
  404) still raise immediately. It is opt-in (off unless called), chainable, and
  the context-wide counterpart of the per-call `execute_query_retry`.
  `ctx.auto_retry` reports whether a policy is active. The policy is stored on
  the pending `ClientRequest` (next to the rate limiter) and is carried over by
  `ClientContext.clone(...)`, which reuses the source request.
- **Permission hints on denied requests:** the per-method `@require_permission(...)`
  declaration (previously documentation-only) now tags the query the method
  builds. When a request is denied, the raised `AccessDeniedException` names the
  declared permission alongside generic remediation (grant the app role and
  admin-consent it, or add the delegated scope; fail fast with
  `require_application_permission(...)` / `require_role(...)`). Other error types
  are left untouched, so the hint never misleads. `ClientRequestException.add_hint`
  / `.hints` let application code append or read custom hints, and
  `ClientRuntimeContext.last_query` exposes the most recently queued query. The
  shared rendering pipeline also backs the SharePoint guidance-bearing errors
  (`FileLockedException`, `SPFileCheckOutException`, `SPQueryThrottledException`),
  so each shows its guidance exactly once.
- **Human-readable identity values:** `UserIdentity` and `Identity` implement
  `__str__`, so a display name (falling back to UPN / IP / object id) prints
  instead of the class name.
- **Domain management:** `client.domains` is now a `DomainCollection` with
  `add(domain_id)`, `get_by_id(domain_id)` and an idempotent `ensure(domain_id)`
  (get-first, because Graph rejects a duplicate domain rather than returning
  it). `DomainDnsRecord.value` surfaces the record's target value
  (`canonicalName` / `text` / `mailExchange` / `nameTarget`), whichever the
  record type uses.
- **Readable runtime objects:** `ClientValue`, `ClientObject`, `ClientResult`,
  `ClientObjectCollection` and `ClientValueCollection` now render themselves, so
  examples can `print(obj)` instead of reaching into a property. `str(obj)` gives
  a natural label (`ClientObject` falls back to `displayName` / `name` / `title`,
  then to `repr`); `repr(obj)` gives a bounded `ClassName(field=value, …)`
  projection that skips unset (`None` / `datetime.min`) fields and truncates long
  values. A collection renders a pandas-style preview of the items **already
  loaded** — it never calls `execute_query`, so `repr`/`str` stay cheap and
  side-effect-free — plus `_repr_html_` for an HTML table in Jupyter. Rendering
  is recursion-safe and depth-bounded (a self-referential object prints `…`).
  Domain label overrides (`Application.__str__`, `UserIdentity.__str__`, …) are
  preserved. Behaviour limits live in `office365.runtime.display`. Dataclass-backed
  values are covered too: `ClientValue.__init_subclass__` seeds `__repr__` before
  the `@dataclass` decorator runs, so the generated `repr` no longer shadows it.
  Call `collection.to_string()` for a full text report — it renders every loaded
  item and does not truncate columns (so identifiers such as a UPN or GUID stay
  intact), unlike the bounded `repr`/`str` preview. A preview is honest about
  completeness: when the server signalled a further page (`has_next`) the count
  is marked `N+` and a "more pages available — call get_all()" hint is appended,
  so `print(collection)` never implies you have seen everything.
- **Credential expiry helpers:** new `Credential` base for `KeyCredential` and
  `PasswordCredential` carrying the shared `is_expired` / `days_until_expiry`
  logic, plus `expiry_status(warn_days=30)` returning a printable
  `CredentialExpiry` (`VALID` / `EXPIRING` / `EXPIRED` / `NO_EXPIRY`) and a
  `kind` label (`"Certificate"` / `"Password"`). `str(credential)` returns its
  display name (falling back to `hint`, then `"(unnamed)"`).

### Changed
- **Planner writes:** Planner entities derive from the new `PlannerEntity` base,
  which sends the `If-Match` header from the latest etag on update/delete and
  requests `Prefer: return=representation` so the refreshed etag is captured —
  consecutive updates no longer fail with a stale-token `409`. Collections route
  writes to the canonical top-level sets: `plan.buckets.add(...)` /
  `plan.tasks.add(...)` `POST` to `/planner/buckets` / `/planner/tasks` and
  listed items update/delete at the top-level item paths, while listing stays
  nested under the plan. Plans listed through `me/planner/plans` are likewise
  addressed at the top-level `/planner/plans/{id}` set, so `plan.buckets` /
  `plan.tasks` resolve there (Graph rejects those navigations under `/me`).
  `PlannerChecklistItems` is now a `ClientValue` map (was
  a `ClientValueCollection` list), and the value modules dropped the `planner_`
  prefix (`office365.planner.assignment`, `.external_reference`,
  `.order_hints_by_assignee`, `.applied_categories`).
- **Report calls now return `ReportResult`** (was `ClientResult[bytes]` for the
  CSV-streaming variants, e.g. `get_email_activity_counts`,
  `get_mailbox_usage_storage`, `get_teams_team_counts`). `ReportResult` is a
  `ClientResult[Report]`, so `result.value` is a `Report` for every report
  method, and it adds `result.to_text()` for decoded text and `result.csv_rows()`
  for parsed rows; use `result.to_bytes()` for the raw CSV.
  `execute_query()`/`execute_query_async()` return the `ReportResult` itself, so
  the calls chain (e.g. `...execute_query().csv_rows()`). The
  `create_report_stream_query` helper is removed (its `create_report_query`
  equivalent already returned a `Report`).
- **The Security API now lives at `office365.security`** (was
  `office365.directory.security`). `microsoft.graph.security` is a top-level Graph
  service — a sibling of `/directory`, which the old path contradicted. Imports
  must be updated: `from office365.directory.security.alerts... import ...`
  becomes `from office365.security.alerts... import ...`. `client.security` is
  unchanged.
- **`TaskStatus` moved to `office365.todo.tasks.taskstatus`** (was
  `office365.intune.print.taskstatus`). The enum models the Microsoft To Do task
  status and is only used by `TodoTask`, so it now sits next to its consumer.
  Update imports accordingly.

### Fixed
- **OData V3 enum serialization:** SharePoint enums are `Edm.Int32` and now
  serialize as their numeric value instead of their member name (which the
  server rejected with *"Cannot convert a primitive value to the expected type
  'Edm.Int32'"*). Graph/OData V4 enums keep serializing as the member name.
- **Taxonomy field `TextField` deserialization:** `TaxonomyField.text_field_id`
  is now bound to the OData `TextField` property, so listing web/list fields no
  longer trips the computed `text_field` getter's assertion
  (`assert text_field_id is not None`).
- **Backup Storage entity hierarchy:** `SharePointProtectionPolicy`,
  `ExchangeProtectionPolicy`, the OneDrive/SharePoint/Exchange browse and
  restore sessions, the drive/mailbox/site protection units and the
  mailbox/site protection rules now extend their CSDL base types
  (`protectionPolicyBase`, `browseSessionBase`, `restoreSessionBase`,
  `protectionUnitBase`, `protectionRuleBase`) instead of `Entity`, so they
  expose the shared properties and lifecycle helpers.
- **`directoryRoles` lookups no longer send `$top`:** the `directoryRoles` feed
  rejects custom page sizes (*"This resource does not support custom page
  sizes"*), but `first` / `first_or_none` / `single` — and the `find_by_name`
  built on them — bounded every lookup with `$top`. The internal `$top` hint is
  now applied only when the collection's declared
  :class:`~office365.runtime.query_capabilities.QueryCapability` accepts it (and
  `DirectoryRoleCollection` declares `$top` unsupported), so the match is bounded
  client-side from the filtered response instead of failing on the wire. An
  explicit `.top(...)` on such a collection now fails fast with a clear
  `QueryOptionNotSupportedError`.
- **Sign-in activity timestamps deserialize to `datetime`:** `SignInActivity.lastSignInDateTime`
  and `lastNonInteractiveSignInDateTime` were annotated `datetime | str | None`, which
  the value converter could not resolve to a scalar converter, so Graph's ISO-8601
  strings were stored verbatim as `str` (while `lastSuccessfulSignInDateTime`
  became a `datetime`). Both fields are now `datetime | None`, so all timestamps on
  the object are parsed consistently — examples comparing them against a cutoff no
  longer need to coerce strings.
- **Request payload scalars are serialized:** a body built from a dictionary or
  list now serializes `datetime` / `date`, `Enum` and `UUID` values instead of
  handing them to the JSON encoder unchanged — `OnlineMeetingCollection.create_or_get(...)`
  no longer fails with `TypeError: Object of type datetime is not JSON
  serializable`. Raw binary bodies (file-upload content) are passed through
  untouched, as before.
- **Declared types of reserved-word properties:** the value converter resolves a
  getter renamed to dodge a builtin (`CallRecord.type` is exposed as `type_`) as
  well as the plain snake-case name, so such a property deserializes to its
  declared type — `CallRecord.type` is a `CallType` member, not the raw JSON
  string.
- **Raw report content is surfaced again:** `ClientResult.set_property("__value", ...)`
  now fills a content-bearing `ClientValue` (`Report.content`) instead of storing
  the value only on the result, so `client.reports...` CSV/JSON responses are no
  longer empty. (`Report.to_bytes()` had been returning `None` for every
  `create_report_query` endpoint.)
- **Teams members use the concrete payload type:** adding a team member posts an
  `aadUserConversationMember` (`@odata.type`, `roles`, `user@odata.bind`) rather
  than the abstract `conversationMember`, and “set role” PATCHes the same type —
  Graph previously rejected both with an unsupported-OData-type error.
- **Teams chat creation carries its topic:** `ChatCollection.add(..., topic=...)`
  includes the topic in the creation payload, so creating a group chat no longer
  fails with “Only 'Topic' must be specified in the request body”.
- **Shared-channel team info serializes concretely:**
  `SharedWithChannelTeamInfo` reports `microsoft.graph.sharedWithChannelTeamInfo`
  instead of the base `teamInfo`, which the `sharedWithTeams` endpoint rejected.
- **Intune errors are readable:** the Intune proxy nests a JSON object (and
  support diagnostics) inside `error.message`; `ClientRequestException.message`
  now unwraps the inner `Message` and drops the ` - Operation ID … - Activity ID …`
  suffix, so `str(exception)` is the actionable sentence
  (`Application is not authorized to perform this operation. Application must have
  one of the following scopes: …`). Plain-text messages from other services are
  unchanged.
- **Intune role assignments are typed:** `DeviceAndAppManagementRoleAssignment`
  now derives from the generic `RoleAssignment`, so `device_management.role_assignments`
  entries expose `display_name`, `description` and `role_definition` alongside
  their `members` — previously only `members` was available.
- **To Do list creation sends its name:** `TodoTaskListCollection.ensure(...)`
  now includes `displayName` in the `POST /me/todo/lists` payload. The property
  was set on the returned object but never marked for persistence, so the first
  `ensure` call failed with *"The property 'displayName' is required"*.
- **To Do attachments/links declare the right OData type:**
  `TaskFileAttachment` reports `microsoft.graph.taskFileAttachment`, so
  `todoTask.attachments.add(...)` creates a file attachment instead of an
  abstract one; `LinkedResource` reports no type (the To Do service cannot
  resolve `microsoft.graph.linkedResource` and rejected creation).
- **URL threat assessments carry the concrete OData type:**
  `UrlAssessmentRequest` reports `microsoft.graph.urlAssessmentRequest` instead
  of inheriting the abstract `microsoft.graph.threatAssessmentRequest` from
  `ThreatAssessmentRequest`. The Graph endpoint rejected the abstract type with
  `InvalidBody`, so `information_protection.create_url_assessment(...)` failed;
  the file and email-file requests were already correct.
- **Planner assignments/checklists are writable:** the assignment and checklist
  Open Type maps serialize as JSON objects keyed by id (previously a list, or an
  empty `{}`), and `PlannerAssignment` / `PlannerChecklistItem` omit the
  server-managed `assignedBy` / `lastModifiedBy` / `lastModifiedDateTime`
  fields that Graph rejects with *Incompatible type kinds were found*.
- **Subject rights requests send a conforming `dataSubject`:** creation now
  builds the subject with `DataSubject` (`microsoft.graph.dataSubject`) rather
  than the never-valid `SubjectRightsRequestIdentity`, which Graph rejected with
  *Invalid OData type specified*.
- **Credential expiry handles naive timestamps:** `PasswordCredential` and
  `KeyCredential` interpret a naive `endDateTime` as UTC in `is_expired` /
  `days_until_expiry` instead of raising *can't subtract offset-naive and
  offset-aware datetimes*; `Application.add_certificate` now stores aware UTC
  timestamps.
- **`GraphClient.has_application_permissions` returns a correct answer:** the
  check now executes the service-principal lookup eagerly (matching
  `require_application_permission` and `has_delegated_permission`) instead of
  evaluating a deferred callback before the app roles were populated, so it no
  longer reports a false negative; it returns a plain `bool` (was a
  non-functional `ClientResult[bool]`).
- **Agreement-file types inherit their properties:** `AgreementFile`,
  `AgreementFileLocalization` and `AgreementFileVersion` now derive from
  `AgreementFileProperties` (the metadata base type) instead of `Entity`, so the
  declared `fileName`, `language`, `isDefault`, `createdDateTime`, … properties
  are populated instead of returning `None`.
- **Graph change notifications serialize correctly:**
  `SubscriptionCollection.add(...)` accepts a plain `resource` string (a
  leading slash is stripped) as well as a `ResourcePath`, and
  `Subscription.expiration_datetime` serializes `expirationDateTime` in UTC `Z`
  form (the generic serializer emitted a numeric offset).
  `client.subscriptions.add(...)` previously produced a payload Graph rejected.

### Added
- **To Do attachment content:** `AttachmentBase.content_bytes` exposes the
  base64-encoded `contentBytes` of an attachment returned by
  `todoTask.attachments`, which yields the base type rather than the concrete
  `TaskFileAttachment`.
- **Sharing-link updates:** `ListItem.share_link` / `File.share_link` /
  `Folder.share_link` accept an optional `share_id` (the `ShareId` returned when a
  link was created). The server then updates that existing tokenized link in place
  — for example to change its expiration — instead of creating a second link for
  the same item. The `update_sharing_link` example now updates the link it just
  created.
- **Declarative OData query-option capabilities:** `@query_capabilities(...)` on a
  `ClientObjectCollection` subclass declares the query options an endpoint rejects
  (or the exact set it allows). The fluent setters — `top`, `skip`, `order_by`,
  `filter`, `select`, `expand`, and therefore `paged` / `get_all` — raise
  `QueryOptionNotSupportedError` for an unsupported option, or warn and ignore it
  with `on_unsupported="warn"`. Applied to `CallRecordCollection`, whose feed
  rejects `$top`, so the `call_records` example no longer sends it. Mirrors the
  `@odata` / `@limit` / `@require_permission` declare-collect-enforce family.
- **Property-level query capabilities and `Prefer` injection:**
  `@query_capabilities(...)` now also accepts `unsupported_filter` / `filterable`,
  `unsupported_orderby` / `orderable` (property deny/allow-lists) and `prefer` (a
  property-to-`Prefer`-header map). A `$filter` / `$orderby` that references a
  rejected property raises `QueryPropertyNotSupportedError` before the request is
  sent (or warns with `on_unsupported="warn"`, keeping the expression — silently
  dropping one side of a filter would change its meaning). A declared `prefer`
  value is attached to the request automatically. Applied to the new
  `DriveItemCollection`: filtering `driveItem.size` is rejected client-side
  (SharePoint maps it to the non-filterable `SMTotalFileStreamSize`), and
  filtering `lastModifiedDateTime` carries the `Prefer` header the service
  requests.
- **SharePoint upload parity:** `Folder.ensure_file(relative_path, content, *,
  on_conflict="skip", chunk_size=...)` is the deferred get-or-upload counterpart
  of `Folder.upload_file` — it creates missing parent folders, then reuses the
  file when it exists (`"skip"`, the default, so a re-run is a no-op) or
  overwrites it (`"replace"`), dispatching to a resumable upload session for
  content above the chunk threshold and returning the file addressed by name.
  `FileCollection.upload_file(path_or_file, file_name=None, *, chunk_size=...,
  progress=...)` uploads a local path (`str`/`os.PathLike` or an open stream) with
  the same size-based dispatch, replacing the manual
  `create_upload_session` / `upload_content` branching.
- **Tolerant writes:** `Entity.delete_object(ignore_missing=True)` and
  `Folder` / `File` / `List` / `ListItem.recycle(ignore_missing=True)` treat a
  missing object (HTTP 404) as success — making cleanup re-runs idempotent —
  while every other failure still propagates. `ViewCollection.ensure_view(...)`
  is the deferred get-or-create counterpart for list views (matched by title;
  `on_conflict="update"` reconciles scalar settings), replacing the hand-rolled
  enumerate-then-create idiom.
- **Bulk collection writes:** `EntityCollection.update_all(*, where=None, **properties)`
  sets properties on every loaded entity and queues one update each;
  `EntityCollection.delete_all(*, where=None, ignore_missing=False)` queues one
  delete each. Both are deferred — load the collection first, then run the queue
  with `execute_query()` or `execute_batch()` to send the writes as `$batch`
  requests. Each accepts an optional client-side `where` predicate, and `update_all`
  also accepts a callable property value derived from each entity (e.g.
  `items.update_all(Title=lambda i: f"{i.properties['Title']} (archived)")`).
  `List.clear()` now delegates to `delete_all()`. Collections whose server API
  already exposes a one-shot `DeleteAll` (comments, file versions, recycle bin)
  keep that behavior; the generic per-item method applies to collections such as
  list items and attachments.
- **Property-bag updates:** `Entity.update_properties(**values)` is sugar over
  repeated `set_property` calls followed by `update()` — it coerces each value
  the same way, queues a single update, and returns the entity for chaining. The
  request stays deferred until `execute_query()`. It is available on both the
  Graph and SharePoint entity bases.
- **Rich field provisioning:** `List.ensure_field(...)` and `ensure_fields(...)`
  now accept a populated `FieldCreationInformation` (or a mix of column names and
  specs), so rich columns — `Choices` for Choice/MultiChoice, `Formula` for
  Calculated, a lookup target, `Required` — are provisioned declaratively and
  idempotently in one deferred pass. `FieldCollection.ensure(...,
  on_conflict="update")` reconciles those rich settings (choices and formula only
  when set; `Required` is only turned on, never off) alongside the field kind and
  description, and now patches the field entity itself rather than an unresolved
  URL. Ensured fields also keep their concrete type (`FieldChoice`,
  `FieldCalculated`, ...), since `Field.resolve_field_type` accepts a `FieldType`
  enum.
- **SharePoint securable-object resolution:** `Web.get_securable_object(scope, *,
  list_title=None, url=None)` resolves, in one deferred call, the web
  (`"web"`/`"site"`), a list (`"list"`), or the list-item facet behind a folder
  (`"folder"`) or document (`"item"`/`"file"`) — raising `ValueError` when the
  scope's required argument is missing. `SecurableObject.grant_access(principal,
  role)` and `revoke_access(principal, role)` are discoverable, chainable wrappers
  over `add_role_assignment` / `remove_role_assignment`.
- **Idempotent lookups & result helpers:** `ClientObject.get_or_none()` and
  `ClientObjectCollection.first_or_none(expression=None)` queue a deferred read
  (run with `execute_query()`) that returns the entity itself instead of raising
  when it is missing — the object is left uninitialized, which the new
  `ClientObject.is_loaded` property (and any typed property being `None`) reports;
  `ClientResult.to_bytes()` / `Report.to_bytes()` normalize binary
  report payloads; `SearchResult.rows` / `RelevantResults.rows` plus
  `SimpleDataRow.get()` / `as_dict()` flatten SharePoint search results; and
  `office365.runtime.progress.progress_bar(description)` is the shared optional
  tqdm hook for long-running operations (a no-op when tqdm is not installed).
- **Consistent two-verb lookups (`get_by_*` vs `find_by_*`):** collection lookups
  now follow one rule. `get_by_<key>` *addresses* an entity for a cheap read (it
  queues nothing on its own; `sites.get_by_url` / `sites.get_by_path` stay the
  documented eager exception), while `find_by_<key>` *searches*: it queues a
  deferred, tolerant lookup that leaves the returned entity uninitialized on a
  miss (check `is_loaded`) instead of raising. Pass `required=True` to opt into
  the strict `single()` semantics (a miss raises `NotFoundException`, an
  ambiguous match raises `ValueError`). New `find_by_*` helpers were added to the
  Graph groups, directory roles, service principals, contact folders, site pages,
  list items, term-store groups and sets, and the SharePoint publishing pages,
  taxonomy groups and content types; the released `get_by_name` / `get_by_title`
  / `get_by_path` resolver names remain as deprecated strict aliases (see
  *Deprecated*). Filter-based finders now share `escape_odata_string`, which
  doubles an embedded `'` in OData string literals.
- **Tolerant Graph lookups:** deferred, non-raising resolvers built on
  `first_or_none` — `UserCollection.find_by_mail(mail)`,
  `TeamCollection.find_by_name(display_name)` (resolved through
  `/groups?$filter=resourceProvisioningOptions/Any(x:x eq 'Team')`, since
  `GET /teams` does not support `$filter`), `BookingBusinessCollection.find_by_name(display_name)`
  (matched client-side, as the Bookings API supports no `$filter`),
  `ManagedDeviceCollection.find_by_name(device_name)` (server-side `$filter` on
  `deviceName`), and `SubscribedSkuCollection.find_by_part_number(sku_part_number)`
  (client-side, case-insensitive). Each returns the entity itself and leaves it
  uninitialized on a miss (check `is_loaded`); `GraphClient.subscribed_skus` and
  `DeviceManagement.managed_devices` now expose these typed collections.
- **Long-running operations (LRO):** a first-class, transport-agnostic
  `OperationPoller` (`office365.runtime.lro`) for the Microsoft Graph async
  pattern — `OperationPoller.from_response(...)` plus blocking `wait()` and
  awaitable `wait_async()`, poll-URL resolution (`Operation-Location` /
  `Azure-AsyncOperation` / `Location` / `original-url`), `Retry-After`-driven
  pacing with automatic `429`/`503` back-off, terminal-state detection, an
  `on_progress` snapshot hook, and serializable `ContinuationToken`s that resume
  an operation in a later call or process. Monitor URLs are polled without
  credentials by default (Graph monitor URLs are unauthenticated and may be
  cross-host); pass `authenticate=True` for services that require it.
- **Waitable Graph long-running operations:** `LongRunningOperationResult`
  (`office365.runtime.lro`) wraps an action's monitor URL with blocking `wait()` /
  awaitable `wait_async()`, and `DriveItem.copy()` now returns a
  `DriveItemCopyResult` whose `wait_for_item()` / `wait_for_item_async()` poll the
  copy to completion and return the new `DriveItem`.
- **Waitable operation entities:** a `PollableOperation` mixin
  (`office365.runtime.pollable`) gives `RichLongRunningOperation`,
  `WorkbookOperation`, `TelephoneNumberLongRunningOperation` and
  `TeamsAsyncOperation` direct `wait()` / `wait_async()` polling, honoring
  `Retry-After`, treating a transient `404` as a "not created yet" gap, and
  raising `OperationTimeoutError` / `OperationFailedError` on failure.
- **Async Teams operation polling:** `TeamsAsyncOperation.poll_for_status_async`
  and `wait_for_operation_async` await an operation on the event loop (no
  blocking), with `Retry-After` pacing and the same `404`-gap tolerance.
- **`Prefer: respond-async` submissions:** `office365.runtime.http.prefer`
  (`RESPOND_ASYNC`, `prefer_respond_async`) and `RespondAsyncRequest`
  (`office365.runtime.respond_async`) submit a query with the OData
  `respond-async` preference (as used by the Excel workbook APIs) and bridge the
  outcome onto the LRO poller — a `202 Accepted` becomes a waitable
  `LongRunningOperationResult`, while a synchronous response fills the query's
  regular result. Sync and async (`execute` / `execute_async`) entry points.
- **Streamed report export:** `ReportRoot.download_report` /
  `download_report_async` (and `office365.reports.report_export`) follow the
  reports API's `302` redirect straight to the pre-authenticated download URL and
  stream the CSV/JSON chunk-by-chunk into a path or binary stream — no full-report
  buffering — returning a `ReportExportResult` with the bytes written and the
  server's `Content-Disposition` file name. `progress` reports bytes as they land.
- **Async/await support:** async twins of the terminal query API —
  `ClientRuntimeContext.execute_query_async`, `ClientObject.execute_query_async`,
  `ClientResult.execute_query_async`, `execute_query_async_retry`, and
  `async with ctx:`. The default transport offloads the blocking `requests` call to
  a worker thread (`BaseTransport.execute_async`), so no extra dependency is needed.
  See `docs/async.md`.
- **Async batching:** `ClientContext.execute_batch_async` and
  `GraphClient.execute_batch_async`, with per-request retry honoring `Retry-After`
  and optional `concurrency`.
- **Async parallel queries:** `ClientRuntimeContext.execute_query_parallel_async`
  (awaitable twin of `execute_query_parallel`) with `concurrency`, retry, and
  `progress`.
- **Async paging:** `ClientObjectCollection.get_all_async(page_size, ...)` and
  `async for item in collection`.
- **Async streaming export:** `RecordCollection.export_to_async` (and
  `List.export_to_async`) streams an appendable format (CSV/TSV/NDJSON/JSON) page
  by page on the worker pool — bounded memory, the loop stays free, and the target
  is closed on cancellation/failure. Without `page_size` the loaded collection is
  written in one offloaded pass.
- **Async pacing parity:** `RateLimiter.acquire_async`/`paced_async` and
  `ThrottledTransport.execute_async`/`aclose`.
- **Async cancellation cleanup:** an aborted parallel run cancels its in-flight
  sibling requests, and both the parallel and sequential drains restore unapplied
  queries and clear the current query so a retry can resume.
- **Async auth offload:** `ClientRequest.before_execute_async` runs `beforeExecute`
  hooks (token/digest/user callbacks) on a worker thread.
- **Async retry:** `retry_async` in `office365.runtime.retry`.
- **High-level bulk download:** `Folder.download`, `FileCollection.download` and
  `File.download` return a `DownloadOperation` — paged/recursive enumeration,
  relative tree, `overwrite=False` resume, bounded concurrency, per-file retry, and
  `DownloadResult.failures`/`stats`/`raise_if_errors()`.
- **`on_error` collector for parallel queries:** `execute_query_parallel` /
  `..._async` accept `on_error=(query, error) -> None`; a permanently failing query
  is reported and skipped instead of aborting the batch.
- **Optional native-async transport:** `HttpxTransport` behind the `[httpx]` extra,
  enabled per request via `ClientRequest.with_async_transport(...)`.
- **Streaming transport contract:** `BaseTransport.stream`/`stream_async` (optional
  `on_headers`), implemented natively by `HttpxTransport`.
- **Async streaming downloads:** `File.download_session_async(stream, ...)` with the
  same `chunk_downloaded`/`chunk_size`/`use_path`/`progress` behavior.
- **Async content streams and lifecycle:** `DriveItem.get_content_stream_async` /
  `File.get_content_stream_async` yield the file body chunk by chunk for piping to
  any destination (socket, second upload, hash) with an optional `on_headers`
  callback, and close the HTTP response on early exit/cancellation;
  `ClientContext.close()` / `await ClientContext.aclose()` release the transport
  when not using `with` / `async with`.
- **Async large-file uploads:** `DriveItem.resumable_upload_async(path, ...)` creates
  the upload session and PUTs every chunk without blocking the loop — each chunk is
  read from disk on the offload executor and sent through the async transport, with
  optional `chunk_uploaded`/`progress` reporting. The reusable
  `UploadSessionRequest.execute_query_async` drives the same chunk loop for other
  upload-session callers. For SharePoint libraries,
  `FileCollection.create_upload_session_async(path, size, ...)` is the awaitable
  twin of `create_upload_session` with the same `chunk_uploaded`/`progress`
  semantics.
- **Tunable async offload executor:** blocking transport work is offloaded to a
  dedicated, lazily-created process-wide pool instead of the event loop's shared
  default executor. Size it with `configure_offload_executor(max_workers=...)`,
  release it with `shutdown_offload_executor()`, or give a transport its own via
  `BaseTransport.offload_executor`.
- **Tunable connection pool:** `with_transport` (Graph and SharePoint) and
  `RequestsTransport` accept `pool_connections`, `pool_maxsize` and `pool_block`
  to size each session's `requests` `HTTPAdapter`. Defaults match `requests`;
  the settings are ignored when a custom `session=` is supplied.
- **Async token callbacks:** `with_access_token` (Graph and SharePoint) now accepts
  an `async def` callback. The async API awaits it on the event loop (single-flight,
  and cached for its `expiresIn`), so token acquisition can use genuinely
  asynchronous I/O; the token is primed before an async batch payload is built,
  whose sub-requests are authenticated synchronously. Requests authenticated this
  way are marked so the offloaded synchronous auth hook skips them, and the
  synchronous API raises a clear error instead of failing with an unreadable token.
  See `docs/async.md`.
- **Async SharePoint migration monitoring:** `MigrationServerJob` gains awaitable
  twins `progress_async` / `all_events_async` / `errors_async` / `status_fn_async`
  / `monitor_async`, so a `GetMigrationJobProgress` ingestion job can be polled
  off the event loop — and several jobs watched concurrently.
- **`Sites.Selected` site access helpers:** `Site.grant_access(identity, roles)`
  and `Site.revoke_access(identity)` (Graph sites) wrap the site `permissions`
  collection so least-privilege, per-site app access reads as
  `site.grant_access(sp, "write").execute_query()`. Both queue their requests and
  resolve on `execute_query`; `revoke_access` removes every permission whose
  grantee matches the given principal, loading an entity identity first so a
  deferred principal works too. App-aware twins `Site.grant_app_access(app, roles)`
  and `Site.revoke_app_access(app)` accept an `Application` entity or an
  application (client) ID and resolve the matching **service principal**
  internally, so the common case is the one-liner
  `site.grant_app_access(client_id, "write").execute_query()`;
  `grant_access` likewise accepts an `Application` and resolves it (site
  permissions reference the service principal object ID, not the application
  object ID). `examples/sharepoint/getting-started/`,
  `examples/sharepoint/auth/setup/certificate_auth.py`, and
  `examples/entraid/applications/grant_site_selected_permission.py` now use them.
- **Idempotent app certificates:** `Application.ensure_certificate(cert_data, display_name)`
  attaches a certificate only when it is not already present — it compares the
  certificate's SHA-1 thumbprint against `keyCredentials.customKeyIdentifier` —
  and accepts DER/PEM bytes, inline PEM text, or a file path.
  `Application.add_certificate` now normalises PEM input to DER (what Entra
  expects in `keyCredentials.key`) and accepts the same forms, so
  `examples/sharepoint/getting-started/setup_sharepoint_app.py` collapses its
  certificate step to `app.ensure_certificate(CERT_PUBLIC, name)`.
  `Application.certificate_thumbprint(cert_data)` exposes the same upper-case
  hex SHA-1 (the value Entra stores and MSAL expects) so setup scripts no longer
  shell out to `openssl x509 -fingerprint` to read it.
- **Certificate auth without a thumbprint:** `with_certificate` (Graph) and
  `with_client_certificate` (SharePoint) now accept an optional
  `public_certificate` (DER/PEM bytes, inline PEM text, or a file path) and make
  `thumbprint` optional. When the thumbprint is omitted it is derived from the
  certificate with stdlib SHA-1 — the same value Entra stores in
  `keyCredentials.customKeyIdentifier` — so no extra dependency is needed and
  self-signed certificates keep working. Pass `use_sni=True` to use subject
  name/issuer authentication instead (PS256 + `x5c`; requires the optional
  `cryptography` package and a certificate issued by a trusted CA). Existing
  `thumbprint=...` calls are unchanged.
- **Idempotent app + service-principal setup:**
  `ApplicationCollection.ensure(display_name, *, sign_in_audience=...)` gets the
  app with that display name or creates it — the name-keyed `ensure(name)`
  convention already used by term store groups and To Do lists;
  `ServicePrincipalCollection.ensure(app_id)` is a get-or-create keyed on the
  application (client) ID. Together they collapse the reuse-or-create dance in
  `tests/setup.py` and
  `examples/sharepoint/getting-started/setup_sharepoint_app.py` to a line each.
  The Entra `Request_ResourceNotFound` code now classifies as
  `ObjectNotFoundException`, so the get-or-create detects a missing service
  principal reliably.
- **Idempotent application-permission grants:**
  `Application.grant_permissions(scope, resource=ResourceName.Graph)` grants this
  app an app role on a resource, and `Application.revoke_permissions(...)` removes
  it — `resource` is an application (client) ID such as
  `MsAppIds.Office_365_SharePoint_Online` or a display name such as
  `ResourceName.SharePoint`. `ServicePrincipal.grant_application_permissions` now
  skips the write when the client already holds the role, and
  `ServicePrincipal.revoke_application_permissions` only deletes the assignment
  for the requested role, so both are safe to re-run and `setup_sharepoint_app.py`
  grants `Sites.Selected` in a single call.
- **Teams creations accept owners:** `TeamCollection.create(...)` /
  `create_and_wait(...)` and `ChannelCollection.add(...)` take `owners=[...]`,
  which Graph requires when a team or a private/shared channel is created in
  application context (otherwise: “A team owner must be provided…”).
- **Async (202) channel creation is awaited:** creating a private or shared
  channel answers `202 Accepted` with a `teamsAsyncOperation`;
  `ChannelCollection.add()` now follows the operation and loads the finished
  channel, so `channel.id` is populated when `execute_query()` returns.
- **`Prefer: include-unknown-enum-members` helper**
  (`office365.runtime.http.prefer.prefer_include_unknown_enum_members`): opt a
  request into future enum members — e.g. `ChannelMembershipType` for shared
  channels reads `shared` instead of `unknownFutureValue`.
- **Denied-request error type:** `AccessDeniedException` (HTTP 401/403) joins
  `DuplicatedObjectException` / `ObjectNotFoundException` / `FileLockedException`
  as a typed runtime error, so callers can `except AccessDeniedException` instead
  of matching Graph codes (`accessDenied`, `Authorization_RequestDenied`) or
  SharePoint's `System.UnauthorizedAccessException` HRESULT by hand. It also
  claims status-only 401/403 responses that carry no JSON body.

### Deprecated
- **Resolver `get_by_<key>` names:** the collection-resolving `get_by_name` /
  `get_by_title` / `get_by_path` helpers now emit a `FutureWarning` and are
  scheduled for removal in v4.0 — use `find_by_<key>(..., required=True)` for the
  same strict behavior (or omit `required` for the new tolerant default).
  Term-store sets' `get_by_name` alias stays tolerant, matching its
  `find_by_name`. These names keep working unchanged otherwise.

### Removed
- **`SubjectRightsRequestIdentity`:** the
  `office365.security.subjectrightsrequests.identity` class is gone. It
  advertised a `microsoft.graph.subjectRightsRequestSubjectIdentity` type that
  does not exist in Graph and was never used by the library; the
  `subjectRightsRequest.dataSubject` property is typed as `DataSubject`. This is
  a breaking import change.

### Documentation
- **Microsoft Purview guided tour:** `examples/purview/` is reorganised by
  surface (`ediscovery/`, `records/`, `sensitivity-labels/`, `subject-rights/`,
  `threat-assessment/`) around a read-only capability-snapshot `quickstart.py`,
  with a guided root README and a README per folder. Every script uses `main()`
  plus `argparse`, layers a pre-flight `require_*` guard with a typed
  `AccessDeniedException` catch, and states exactly which permission or
  administrator role it needs.
- **Async discoverability:** the README now has an "Async / await" section and
  table-of-contents entry, the docs landing page lists the async guide in its
  reading path and *What you get*, and `docs/async.md` opens with a note that sync
  is the default and lifecycle hooks are synchronous.
- **Long-running-operations guide** (`docs/long-running-operations.md`): the
  end-to-end story for the Graph async pattern — the raw `OperationPoller`,
  waitable results and operation entities, `Prefer: respond-async`, the status
  vocabulary, continuation tokens, batch-vs-LRO guidance, and the out-of-band
  pattern for SharePoint work that has no REST status endpoint.
- **Async example catalog:** practical scripts across the whole surface —
  `examples/async/` `copy_drive_item_async.py`, `wait_team_clone_async.py`,
  `workbook_operation_async.py`, `resume_operation_async.py`,
  `lro_in_batch_guard.py`, `export_report_async.py`, `stream_download_async.py`,
  `client_lifecycle_async.py`, `tune_offload_executor.py`, `retry_async.py`,
  `page_users_async.py`, `delta_sync_async.py`, `upload_large_file_sp_async.py`,
  `entra_token_cache_async.py`, `copy_queue_worker_async.py`,
  `provision_teams_async.py` and `archive_old_files_async.py`, plus
  `examples/sharepoint/migration/monitor/monitor_async.py`,
  `examples/reports/export_usage_async.py`,
  `examples/onedrive/files/copy_and_wait.py` and `examples/teams/administration/clone.py`.
- **SharePoint getting-started onboarding:** `examples/sharepoint/getting-started/`
  adds a full-cycle `setup_sharepoint_app.py` (reuse/create the app registration,
  attach a self-signed certificate, grant `Sites.Selected` with admin consent,
  grant per-site access, print the connection values) plus a first-call `hello_sharepoint.py`
  and a walkthrough that answers the app-registration, certificate, and
  permission-scope questions. The SharePoint product README is now a guided hub
  (start here → common tasks → full catalog), and the auth pages cross-link it.
- **Teams examples guided tour:** `examples/teams/` is reorganised by resource
  (`administration/`, `members/`, `channels/`, `chats/`, `apps/`, `tags/`,
  `audit/`, `governance/`, `export/`, `migration/`) with a new `quickstart.py`,
  a guided root README (basics → popular tasks → audit/governance → export/migration)
  and a README per folder. Every script was made runnable end-to-end (argparse
  defaults, temp-dir outputs, missing-scope hints that exit cleanly) and the
  duplicated usage reports / call-records / online-meeting scripts moved to
  `examples/reports/` and `examples/communications/` instead of being duplicated.
- **Usage-reports tour:** `examples/reports/` is reorganised by workload
  (`mail/`, `files/`, `teams/`, `apps/`, `security/`, `copilot/`) with a new
  tenant-snapshot `quickstart.py` and a README per folder. The scripts decode the
  report CSV with `utf-8-sig` (Graph prepends a BOM), target the correct
  report/columns, keep outputs in the temp directory, and handle throttling and
  concealed report data gracefully.
- **Microsoft To Do guided tour:** `examples/todo/` is reorganised by resource
  (`lists/`, `tasks/`, `attachments/`, `maintenance/`) around a new `quickstart.py`
  and a read-only `overview.py`, with a README per folder. The scripts cover task
  lifecycle (due dates, importance, recurrence, complete/reopen), server-side
  filtering, checklist items, file attachments, linked resources and bulk cleanup
  of old completed tasks. Every script runs end to end with argparse defaults,
  keeps output in the temp directory, and turns missing-scope errors into a
  one-line hint.

### Fixed
- **Sharing-link expiration rejected as an invalid date:** `ListItem.share_link`
  serialized the `expiration` argument with `datetime.isoformat()`, emitting a
  numeric UTC offset plus microseconds (for example
  `2026-10-16T17:29:49.638704+00:00`). The `ShareLink` endpoint parses that field as
  a wire date-time and rejected it with `System.FormatException: String was not
  recognized as a valid DateTime`. Expirations are now normalized to UTC with
  second precision and a trailing `Z` (new `iso_z` helper).
- **Webhook subscription expiration format:** `SubscriptionInformation.to_json`
  and `Subscription.expiration_datetime` serialized the date with
  `datetime.isoformat()`, emitting microseconds (and a `+00:00` offset for an
  aware value). The field is an `Edm.DateTime`, so both now use the UTC `Z` form
  (`iso_z`).
- **`Group.created_datetime` returns `None` when absent:** it previously returned
  the `datetime.min` sentinel (a naive year-1 datetime), which silently corrupted
  age comparisons and formatting. It is now `Optional[datetime]` — `None` when the
  group carries no timestamp, an aware UTC `datetime` otherwise — matching the
  timestamp accessors that already return `None`. Example code can now compare
  `group.created_datetime` directly without a sentinel guard.
- **Nested OneDrive folder addressing:** `ChildrenPath.collection` returned
  `None` for an item addressed by id (`EntityPath(id, items)`), so the next
  `/children` segment collapsed a grandchild to a bare `/{id}`. Nested
  `get_folders` / `get_files` (`recursive=True`), `download_folder` and any
  `items[id].children` chain now keep the canonical `/items/{id}` parents.
- **`DriveItem.ensure_folder` / `ensure_file` on a folder addressed by id:** the
  get-or-create walk used path-based addressing (`/items/{id}:/name:/`) for its
  existence reads, which Microsoft Graph rejects (`Resource not found for the
  segment`). Folder levels and the file leaf are now resolved through the
  parent's `children` collection (`$filter=name eq '...'`), so the ensure
  helpers work whether they start from the drive root or a folder by id.
- **Examples no longer require tqdm:** gallery scripts now use
  `office365.runtime.progress.progress_bar` instead of an unguarded
  `from tqdm import tqdm`, so they run (just without a bar) when tqdm is absent.
  A new `progress` extra installs it, and it is also included in `examples`.
- **Contextvars preserved across offloaded async work:** every blocking call
  handed to the offload pool (transport sends, streaming reads, `beforeExecute`
  hooks, batch execution, file I/O, exports and uploads) now runs inside the
  caller's `contextvars` context, so tenant/correlation ids and logging filters
  survive the thread hop instead of silently disappearing.
- **`single()` no longer downloads every match:** the bounded lookup now sends
  `$top=2` (previously unbounded), so an ambiguous match is rejected after two
  rows instead of materializing the entire result set.
- **Single quotes in OData string literals:** `ODataPathBuilder` doubled a `'` twice
  (`d'appello` became `d''''appello`), so paths and names containing an apostrophe
  resolved to the wrong resource. A quote is now doubled once (#1052).
- **Certificate reuse detection:** the SharePoint setup scripts compared a
  **base64**-encoded SHA-1 thumbprint against Entra's **hex**
  `customKeyIdentifier`, so an already-attached certificate was treated as
  missing and re-uploaded on every run. `Application.ensure_certificate` and
  `tests/setup.py` now compare the upper-case hex form.
- **Graph device-flow sign-in prompts once:** `AuthenticationContext.with_device_flow`
  reuses the account via `acquire_token_silent` before starting a new device flow.
- **Chat members after creation:** `ChatCollection.add` uses a shared placeholder
  path so `members` resolves to `/chats/{id}/members` once the id is assigned.
- **Batch GETs after `File.get_content()`:** `BatchQuery` treats `FunctionQuery` as a
  GET, so it is placed outside the change set; the v3 batch response parser also
  splits sub-responses at the header/body separator and keeps the body as raw bytes
  so binary downloads survive ([#871](https://github.com/vgrem/office365-rest-python-client/issues/871)).
- **Multi-phase writes in SharePoint batches:** `ClientContext.execute_batch` /
  `execute_batch_async` drain the queue in dependency order, resolving each
  `DeferredOperationQuery` barrier so its handlers enqueue the next round, and fire
  per-query `before_execute`/`after_execute` handlers. A query targeting
  `/_api/$batch` is flagged `batchable = False` and run on its own. Fixes
  `DocumentSet.create(...)` followed by `execute_batch()`
  ([#868](https://github.com/vgrem/office365-rest-python-client/issues/868)).
- **List item creates in batches:** `ListItem.ensure_type_name` now defers the
  queued create until `ListItemEntityTypeFullName` is read, so an `add_item` /
  `update` batched via `execute_batch` is serialized with the correct
  `SP.Data.<List>ListItem` annotation instead of the open `SP.ListItem` type.
  Fixes "An open collection property ... was found"
  ([#717](https://github.com/vgrem/office365-rest-python-client/issues/717)).
- **Thread-safe default transport:** `RequestsTransport` now keeps one
  `requests.Session` per thread instead of sharing a single session, so parallel
  and offloaded async requests no longer race on one connection pool.
  `reset_connections()` resets only the calling thread's pool, and `close()`
  releases every session the transport created.
- **Certificate path from a nested working directory:** `tests/settings.py`
  resolves a relative `OFFICE365_CERT_PATH` (documented as
  `tests/selfsigncert.pem`) against the repository root, so examples and tests
  that use app-only certificate auth run from any directory.
- **Transport-level TLS verification and proxies are applied:** `with_transport(
  verify=False)`, `with_transport(proxies=...)`, and a custom CA bundle set on a
  supplied `session` now reach `requests`. `RequestOptions.verify` defaults to
  unset (`None`), so it no longer forces `verify=True` and silently overrides the
  transport/session value; a per-request value still wins.
- **`httpx` per-request `NO_TIMEOUT`:** the sentinel is translated to httpx's
  "no timeout" instead of being forwarded verbatim (which raised `TypeError`).
- **Streaming export stayed bounded-memory:** `RecordCollection.export_to(...,
  page_size=...)` iterated the collection while reading each page, which ran the
  synchronous paging generator and pulled every page inside the first `page_loaded`
  callback. It now appends only the newly loaded `_data` per page, so the export
  actually streams instead of materializing the whole collection.

### Internal
- **Developer onboarding rework:** credentials flow through `tests/settings.py` with
  per-flow readiness checks (`delegated`, `delegated-ropc`, `app-only`,
  `app-only-cert`), `python -m tests.doctor`, and `--require <flow>` gating; live
  tests auto-skip when credentials are missing. `.env.example`, `README-dev.md`,
  `CONTRIBUTING.md` and the example quick starts were rewritten, and the dead
  `office365_python_sdk_securevars` reference removed.
- **Setup automation:** `.env.example`/README-dev document the existing
  `examples/entraid/applications/` and `examples/sharepoint/auth/setup/` scripts;
  `certificate_auth.py` prints a paste-ready `.env` block, `applications/create.py`
  gains `--keep`/`--name`, and `rotate_cert.py` uploads a configurable public
  certificate.
- **Certificate setup for Graph:** `applications/rotate_cert.py` gains `--generate`;
  docs say "SharePoint REST API v1" instead of `/_api`.
- **Guided credential setup:** `python -m tests.setup` reads `.env`, prompts only for
  the missing tenant/app id, reuses or creates app credentials, derives the
  SharePoint URLs, and writes `.env` (with `.env.bak` and `--dry-run`). It now also
  asks whether to create a client secret (default no; `--with-secret`/`--no-secret`
  force it; `--yes` keeps it off) and prints how to add one later. Generated
  certificates are no longer tracked.
- **Two-user test model:** `OFFICE365_TEST_USER1`/`OFFICE365_TEST_USER2` replaced by
  `OFFICE365_USERNAME` and optional `OFFICE365_USERNAME_ALT`; `tests/__init__.py`
  still exposes `test_user_principal_name`/`test_user_principal_name_alt`.

### Documentation
- **The Intune examples are now a lifecycle-guided tour.** `examples/intune/` is
  organised by where a device is in its Intune journey — enrol (`enrollment/`),
  register (`devices/`), configure (`policies/`), protect (`apps/`), govern
  (`reports/`), audit (`audit/`), administer (`administration/`, `protection/`) —
  with a Mermaid lifecycle diagram in the root README explaining how the stages
  connect and which of the two Intune singletons (`device_management` vs
  `device_app_management`) owns each resource. New scripts cover enrolment
  configurations and Autopilot, compliance/configuration rollups, protection
  connectors (with stale-heartbeat flags), long-running export jobs, audit
  events, RBAC and device categories. Every script runs against a live tenant,
  is scope-gated (a missing permission prints the exact scope and exits `0`),
  defaults to delegated auth, and writes outputs to the system temp directory.

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
