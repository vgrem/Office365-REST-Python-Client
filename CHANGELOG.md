# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/),
and this project adheres to [Semantic Versioning](https://semver.org/).

## [Unreleased]

### Added

**Model metadata**

- Generated Graph getters now declare their OData wire name in place
  (`@odata(name="iCalUId")`, `office365.runtime.types.odata_property`), so nothing
  spells a wire name twice and the awkward ones resolve:
  `declared_type(Event, "iCalUId")` answers `str` where it used to answer `None`
  (a `to_snake_case` guess spells it `i_cal_u_id`). `ODataPropertyMeta.navigation`
  marks a CSDL `NavigationProperty` — the ones `$expand` reaches and `$select`
  cannot name — so `Event.attachments` is distinguishable from a column.
  `office365/outlook` is fully declared: `scripts/mark_odata.py` back-fills the
  declaration onto files the generator will not re-render (it only renders members
  that are missing), and `generator/templates/graph` emits it for new ones — with a
  value or enum type a getter constructs imported at module level instead of under
  `TYPE_CHECKING` only, so the annotation a new file gets is resolvable at run time. A
  declaration that exists but says less than the metadata — a navigation property
  without the flag, as every previously-hand-marked getter had — is finished in
  place. The declarations are answerable at runtime, so a projection is derived
  rather than hand-written: `Event.select_all()` returns the 41 wire names `$select`
  accepts (navigation properties excluded, `id` included via `Entity`),
  `Event.expandable()` returns the 7 `$expand`-only ones, and
  `Event.wire_name("ical_uid")` answers `"iCalUId"` rather than the snake-case
  misspelling; an attribute with no declaration raises `AttributeError` listing the
  ones that do. Declaring an enum-typed property makes a read answer with the
  generated enum member instead of the raw string; `CalendarSource` compares `type`
  through the member name, so calendar exports are unaffected.
- Every column a served module declares now resolves a declared type: `declared_type(Event, "start")`
  answers `DateTimeTimeZone` where it answered `None`. Twelve getters that construct a value
  object carried either no return annotation (`Event.start`/`end`/`body`/`location`/`attendees`,
  `Calendar.owner`, `Place.address`) or one naming a type imported only under `TYPE_CHECKING`
  (`Event.onlineMeeting`, `Room.bookingType`/`teamsEnabledState`, `Workspace.mode`,
  `EventMessage` dates/location/type, `Post`, `Person`, `ProfileCardProperty`,
  `CheckInClaim`); both left hydration reading a bare dict where the model promises a value
  object. `converters.value` now distinguishes an unresolvable annotation from a resolution
  failure instead of swallowing every exception, and a test fails if any `$select` column of a
  served package stops declaring its type.

**Migration (identity)**

- `IdentityMap` (`office365.migration`) maps source principals onto target
  principals for authorship and ACLs, so a run can cross tenants (or follow a
  login rename) without hand-editing the payload: entries from a CSV
  (`source,target[,system_id]`), plus e-mail domain rewrites (`contoso.com` →
  `fabrikam.com`, keeping the claims prefix) and an unmapped policy
  (`skip` / `fail` / `fallback_owner`). The engine applies it to `item.author`,
  `item.editor` and every `PermissionEntry` for both the REST and server-side
  package targets, and a remapped principal drops the source PUID (a PUID only
  means something in its own tenant) unless the CSV supplies the target one.
  Unmapped principals are never silent: they are collected in `IdentityMap.unmapped`
  and reported in the run summary (`identity_mappings`, `identity_rewritten`,
  `identity_unmapped`, `identity_unmapped_principals`, `identity_policy`).
  `MigrationSettings.user_mapping_file` now feeds it, and `automatic_user_mapping=False`
  turns mapping off — both were previously listed as unhonored settings. There is
  no directory lookup and groups are still not mapped.

**Migration (mail)**

- `MailFolderSource` + `MailExportTarget` (`office365.migration.outlook`) export a
  mail folder and its subtree as a portable EML tree through the existing
  `MigrationJob`: one `.eml` (RFC 822 bytes) plus one JSON sidecar per message —
  the sidecar keeps what MIME cannot (Graph ids, read state, Outlook categories,
  conversation id, folder path) — and a `manifest.jsonl` index. Destinations are
  derived from the message (`date_subject_id-digest.eml`), so a resumed run skips
  what is already on disk and `verify()` compares each file's MD5 against the
  source MIME. `MailExportOptions` controls subfolders, drafts and extra
  projection properties.
- `EmlTreeSource` + `MailboxTarget` import that tree back into a mailbox folder
  through Graph's MIME import, recreating the folder chain with the exported
  names, skipping messages the folder already has (matched by
  `internetMessageId`) and replaying read state, categories and importance with
  one `PATCH` per message (`MailImportOptions` turns that off). Verification uses
  the new `mime_digest` — semantic headers plus a hash per decoded part — because
  Exchange re-serializes every message and an imported message is never
  byte-identical. Exchange limits, all reported rather than hidden: an imported
  message is a draft (`isDraft` cannot be cleared by `PATCH`), `receivedDateTime`
  is the import time (the original survives as `sentDateTime`), timestamps are not
  restorable (so `preserve_timestamps` is refused up front), and messages over
  4 MB are refused instead of truncated.
- `MigrationItem.metadata` carries adapter-defined envelope attributes into the
  manifest, so an export writes its own index from the plan instead of re-reading
  the source.

**Migration (calendar)**

- `CalendarSource` + `IcsExportTarget` (`office365.migration.outlook`) export a
  Graph calendar as a portable ICS tree through the same `MigrationJob`: one `.ics`
  (iCalendar, CRLF and RFC 5545 folded, with `TZID`, `RRULE`, `VALARM`, `X-ALT-DESC`
  for HTML bodies) plus one JSON sidecar per event, and a `manifest.jsonl` index.
  The document is rendered from the event record, so `verify()` is an exact byte
  checksum. A recurring event exports once as its series master (occurrences and
  cancellations are opt-in: importing both a series and its instances would
  duplicate every meeting), and Graph's own `recurrence` object travels in the
  sidecar so an import can replay it without parsing `RRULE`.
- `IcsTreeSource` + `CalendarTarget` import that tree back into a calendar through
  the same `MigrationJob`, recreating each event — and each series as a
  `seriesMaster` with Graph's own `recurrence` object — from the sidecar, which is
  the import contract (an `.ics` alone is refused: iCalendar cannot carry the
  recurrence object, so replaying a series from the document would silently turn
  every meeting into a single event). The payload is posted as a Graph-spelled dict
  through a raw `CreateEntityQuery`, because `EventCollection.add()` rewrites
  `timeZone` to `UTC`, drops `transactionId` and rejects a dict `start` (all three
  measured). A re-run skips what it already created — a created event comes back
  with `iCalUid: null` and a fresh id, so the target matches on
  `(subject, wall clock, zone)` and lets two source events that share all three
  import as two — and a deterministic `transactionId` makes two concurrent runs
  collide on the server, where the collision is adopted rather than failed.
  `CalendarImportOptions` decides what is restored: attendees are **opt-in**
  (`restore_attendees=False`, because creating an event with attendees makes
  Exchange send a real invitation to each of them, and `responseRequested: false`
  does not suppress it — measured), categories are on, and the run reports how many
  attendee entries it left out. Verification is `event_digest` — the restorable
  fields, with the service-owned ones and the body markup excluded — because
  Exchange re-serializes the event.

**Migration (contacts)**

- `ContactSource` + `VcfExportTarget` (`office365.migration.outlook`) export a
  contact folder and its child folders as a portable vCard tree through the same
  `MigrationJob`: one `.vcf` (vCard 3.0, CRLF and folded at 75 octets) plus one JSON
  sidecar per contact, and a `manifest.jsonl` index. The document is rendered from
  the contact record, so `verify()` is an exact byte checksum, and the file name
  carries a hash of the Graph id — a contact has no `internetMessageId` and no
  `iCalUid`, so nothing the source knows survives an import. `ContactExportOptions`
  controls the root name, the child-folder walk and extra projected properties.
- `VcfTreeSource` + `ContactTarget` import that tree back into a contact folder,
  recreating the folder chain with the exported names and replaying every office
  field, both addresses, the phones, the IM addresses, the children, the notes and
  the categories — the `.vcf` is what another client opens, the sidecar is what the
  import restores, and an `.vcf` without one raises instead of importing a thinner
  contact. The create body is built locally and posted raw, because
  `ContactCollection.add()` takes four arguments and drops the rest (measured).
  A re-run skips what the folder already has — a contact has no `transactionId`, so
  the target matches on `(display name, first address)` instead, which also means
  two concurrent runs can import the same contact twice (documented, not hidden) —
  and verification is `ContactRecord.digest()`, a digest of the restorable fields read back
  through a fresh handle, because Exchange normalises a birthday's time of day and
  fills in a missing e-mail `name`. Reported rather than assumed: a photo is out of
  scope on both sides (the entity exposes no `hasPhoto` column, so detecting one
  costs a `GET /photo` that 404s per contact) and timestamps are not restorable (so
  `preserve_timestamps` is refused up front). A category containing a comma is
  refused client-side with the offending name, since Exchange rejects the whole
  contact (`ErrorPropertyUpdate`) and the message names neither the field nor the
  value.

**Migration (fidelity forecast)**

- `MigrationJob.plan()` now states the fidelity forecast before it enumerates: one
  `plan.fidelity` event carrying the per-dimension matrix and the reason for every
  dimension that is not `delivered`. `MigrationJob.fidelity()` returns that cached
  report (it never raises). `export_reports` writes a new `FidelityReport` — one row
  per dimension with its status and reason — and the summary row gains
  `fidelity_ok`/`fidelity_summary`, so the run's promise sits in the hand-off pack
  next to its results instead of nowhere. The `versions` reason now states what the
  service actually does with history: every version is stamped with the file's
  `TimeLastModified`, because per-version dates in the manifest are ignored
  (measured on a live ingestion job).

**Migration (bundles)**

- `SharePointPackageTarget` accepts a captured list structure (`sp_list=` +
  `structure=`) and replays it over REST **before** the ingestion job. The manifest
  carries a file's list item, not the library's columns, content types, views or
  container settings, so a package target built by hand (`migrate_library_serverside.py`,
  a bundle produced on another machine) used to ingest into a bare library: field
  values whose columns did not exist were silently dropped. `configure()` — the hook
  the runner calls before the first write — now applies the snapshot through
  `provision_list_structure`, `commit()` repeats the guard for a hand-built job, and
  `on_conflict="skip"` makes both a no-op on a re-run; whatever the target cannot
  reproduce is reported on `target.warnings` instead of being assumed. Live-verified:
  a bare library gained the captured `ProjCode` column with no warnings, and a second
  call wrote nothing. A task resolved by `resolve_task` already replays the structure
  itself and does not pass one.
- A library export can be **re-imported into a library that has none of its shape**.
  `save_list_structure` / `load_list_structure` read and write the bundle's sidecar
  (plain `ListStructure.to_dict()` JSON, the same file `capture_structure.py`
  writes), and `SharePointLibraryTarget` / `SharePointListTarget` accept it as
  `structure=`. Before, the content half of a bundle imported fine and the shape half
  was simply absent: a file uploaded into a bare library carries no column values and
  a record naming a missing column loses it. The snapshot is replayed by
  `configure()` — the runner's pre-write hook — so a directly-built target provisions
  too, a re-run is a no-op, and a `content_type_map` passed to the record target is
  filled in place so records land under the recreated content types. Keep the sidecar
  *beside* the content directory, not inside it: a files source migrates every file
  it finds. Live-verified end to end through `migrate_library.py` (which now writes
  the sidecar on export and auto-detects it on import): a bare target library had no
  `CostCenter` column, gained it on import, and verified
  `OK | source: 1, target: 1, checked: 1, missing: 0, extra: 0, issues: 0`.

**Migration (group ACLs)**

- The server-side package target grants **SharePoint groups** as well as users: a
  role assignment whose member is a `PrincipalType.SharePointGroup` is captured
  with its **title** (`PermissionEntry.principal_type="group"`, `display_name` =
  the title, since the normalized `default:Members` name matches nothing on the
  target) and emitted as a `UserGroup.xml` `<Group>` plus a `PrincipalId` grant.
  Previously the docs claimed groups were skipped — live-verified they are not
  skipped, they were simply never attempted. A `<Group>` **must** name an `Owner`:
  an ownerless one fails the *entire* ingestion job at schema validation
  (`The required attribute 'Owner' is missing`), not just that grant, so
  `PermissionEntry` gained `owner` (a user with a PUID) and `owner_groups` (the
  owner chain, nearest first — a group's owner may be another group, as a site's
  `Visitors` group is owned by its `Owners` group, which owns itself). A group with
  no readable owner is written self-owned rather than dropped or allowed to fail
  the job. Distribution lists, security groups and unresolved principals are still
  skipped with a warning: they are not site groups and do not match by title.

**Long-running operations**

- An operation is now **watchable, not just waitable**: `OperationPoller.stream()`
  / `astream()` (and the same pair on `LongRunningOperationResult`) yield every
  `OperationStatus` snapshot, the terminal one last, and raise nothing for a
  failed or cancelled outcome — `wait()` is the same loop with the failure policy
  applied. Abandoning the loop stops polling.
- `OperationStatus` carries the operation's **timeline**: `created_date_time` and
  `last_action_date_time` (timezone-aware, UTC when the service sends no offset,
  so `now - last_action_date_time` is a stall check rather than a wall-clock mix)
  and `retry_after` (what the poll response asked for). A `partiallySucceeded`
  operation is **terminal but neither outcome** — SharePoint copy and migration
  jobs report item-level failures that way, and it used to be an unknown status,
  i.e. polled until `OperationTimeoutError`; `wait()` now returns it and
  `status.is_partially_succeeded` reports it.
- `RespondAsyncRequest.execute()` / `execute_async()` return an operation **either
  way**: a pollable one when the service accepted `202`, and one that is already
  terminal (no monitor URL, `wait()` answers without a request) when the service
  completed the call in the submitting round-trip. `Prefer: respond-async` is a
  preference, so a caller opting in had to branch on which answer it got — and
  `None` also meant "no operation", which is indistinguishable from "it is
  already done". `LongRunningOperationResult.completed(...)` is the new
  constructor for the settled case, `is_completed` says which one you hold, and a
  repeat `wait()` on a terminal operation no longer re-polls.
- One **engine** behind every wait: `office365.runtime.operation.Operation` owns the
  deadline, `Retry-After` pacing, jitter (`jitter=`), the progress hook, cooperative
  cancel (which wakes a blocked `wait()` in another thread, or on the loop) and the
  rule that a stream raises nothing; a family supplies what one poll *is*
  (`_step` / `_step_async`) and what `wait()` hands back (`_outcome`).
  `OperationPoller` (monitor URL) and `PollableOperation` (operation entity) are
  specialisations of it, and `transient_statuses=` is data: which HTTP codes mean
  "poll again" is a constructor argument, not a branch.
- `PollableOperation` gains `stream()` / `astream()` and `cancel()` /
  `cancel_async()`, which it had neither of. Its `404` gap is now an *attempt, not
  an observation*: the wait retries it at `next_poll_delay()` and does not tell the
  progress hook that the entity did anything.
- `MigrationServerJob.job_wait()` (and `SharePointPackageTarget.job_wait()`) returns
  the wait on an ingestion job instead of running it — a `MigrationJobWait`, so a
  caller can stream the polls (`percentage_complete` per snapshot), cancel the wait,
  or monitor several jobs concurrently in one event loop. A sync `status_fn` given
  to an async wait is bridged with `asyncio.to_thread` (the read is a blocking GET).
- `TeamsAsyncOperation.poll_for_status()` accepts any status as the thing it waits
  for (`status_type`, default `succeeded`) and now ends on a status that says the
  named one will never arrive (`failed`) as well as on the deadline — so it fires
  exactly one callback instead of continuing to poll a job that already failed.
  Both pollers are the shared wait, so `poll_for_status` also gained a real
  `cancel()` and the stream.

### Changed

**Transports**

- The bundled transports now bound the read phase as well as the connect phase:
  the default timeout is `(10 s connect, 300 s read)` for `RequestsTransport`
  and `10 s connect / 300 s read / 300 s write / 10 s pool` for
  `HttpxTransport` (`DEFAULT_READ_TIMEOUT`, `DEFAULT_WRITE_TIMEOUT`,
  `DEFAULT_POOL_TIMEOUT`). A server that stops responding mid-response now
  fails with a transient transport error (`ConnectionError`/`Timeout`, so
  `with_auto_retry` retries it) instead of blocking the caller forever —
  previously only the connect phase was bounded. The read bound
  is a per-byte gap, not a total-transfer bound, so a long upload or download
  that keeps moving is unaffected. Override it per transport (`timeout=(10, 600)`)
  or per request, and pass `NO_TIMEOUT` to remove it.

**Migration**

- `MigrationJob.plan()` now fails fast on a requested fidelity flag the adapter pair
  cannot honor — before the enumeration, with the runner's own message — instead of
  planning the whole source and raising at the first write. A caller that plans with
  `preserve_versions`/`preserve_timestamps`/… on an unsuitable pair now sees
  `NotImplementedError` one phase earlier.
- **`MigrationItem` no longer carries `author_id`/`editor_id`** (breaking). Those were
the site-local numeric ids the *source* used (`AuthorId`/`EditorId`), kept on the
item only because nothing else could hold them; they now live where the rest of the
identity does, as `Principal.user_id` on `item.author`/`item.editor` — set by the
adapters from the same id they already resolved, so the change costs no requests.
A `Principal` is the identity that travels (`system_id` is what `UserGroup.xml`
writes) and `user_id` is scoped to its site, which is exactly why it does not
deserve an item field. The `ItemReport` keeps its `author_id`/`editor_id` columns,
now read from the principal, so report consumers are unaffected; the one visible
difference is that an item whose author could not be resolved reports an empty
column instead of an id that no principal carries. Constructing a `MigrationItem`
with `author_id=`/`editor_id=` now raises `TypeError` — pass
`author=Principal(..., user_id=…)` instead.

**Migration (calendar)**

- **The calendar's spelling, its document and its record are three modules.**
  `calendar_profile` holds the ten tables that decide which iCalendar token a Graph
  word becomes (`showAs` → `TRANSP`/`STATUS`, `sensitivity` → `CLASS`, `importance` →
  `PRIORITY`, attendee type → `ROLE`, response → `PARTSTAT`, weekday/index/frequency →
  `BYDAY`/`BYMONTH`, body content type → `X-ALT-DESC`/`DESCRIPTION`), plus the two
  partial ones whose absence *is* the token — a busy event carries no `TRANSP`, an
  accepted attendee no `STATUS` — and `COMPARED`, the ordered table that decides what a
  verification digest sees and which options gate each field. `calendar_codec` writes the
  document: escaping, folding at 75 octets, the `DTSTART`/`DTEND` pair, `RRULE`,
  `VALARM`, `X-ALT-DESC`. `calendar_models` derives the four import artefacts. A Graph
  enum that gains a member is now a row in a table, and a test fails if a row names a
  member the generated enum does not declare or if a table meant to be complete misses
  one — the two failures that used to be silent (a token for a word nothing sends, a
  value that renders as nothing). The exported bytes are unchanged: a golden test pins
  the document byte for byte.
- **A calendar sidecar is the event as the model serializes it**: `Event.to_json()` plus
  the three keys no model can know (`calendar_path`, `calendar_display_path`,
  `ics_path`), the same shape the contacts sidecar took. So nothing lists a field: a
  column the model declares is exported, replayed and verified with no function edited,
  and the keys are Graph's own (`id`, `iCalUId`, `isAllDay`, `showAs`,
  `attendees[].status.response`, `onlineMeeting.joinUrl`) rather than a snake_case copy —
  which also means a tree exported by a pre-release build is refused with a message
  saying so, instead of importing as a wall of empty fields. `CalendarEventRecord` is
  gone: it existed to *re-spell* the model into `show_as`/`is_all_day`/`graph_id`, so
  with the sidecar being the model's own JSON it was a third representation with nothing
  left to do. A sidecar is now read by functions over `(envelope, options)` —
  `event_ics`, `event_create_payload`, `event_dest_path`, `event_dedup_key`,
  `event_digest`, `event_dropped_attendees`, `event_transaction_id`, `event_key` — which
  is what the adapters call and what callers outside this package already import.
  `ContactRecord` stays: unlike the calendar record it never re-spelled anything (its
  payload has been the model's JSON since `fa2977db9`), so it is a payload plus its
  derived artefacts rather than a second vocabulary. The digest is unchanged
  (`4a8cc8de…`): the canonical form compares the same values, read from Graph's keys.

**Migration (contacts)**

- **A contact's sidecar record is the contact as Graph spells it**: `Contact.to_json()`
  plus the three keys a model cannot know (`folder_path`, `folder_display_path`,
  `vcf_path`). The keys are therefore Graph's camelCase (`displayName`,
  `emailAddresses`, the phone lists, `businessAddress` with
  `postalCode`/`countryOrRegion`) and the id column is `id`, not a snake_case copy with
  `graph_id` — so a sidecar written by a pre-release build is not readable by this one.
  The functions that read that record — `contact_envelope`, `contact_vcard`,
  `contact_create_payload`, `contact_dest_path`, `contact_dedup_key`, `contact_digest`,
  `contact_key` — are now the methods of one `ContactRecord`: `of(contact, folder)`
  during an export, `from_json(sidecar)` to read it back, then `to_json()`, `vcard()`,
  `payload()`, `dest_path`, `dedup_key`, `digest()` and `id`. The record holds a payload
  and where it came from, never an entity, which is what lets an import verify a sidecar
  against a contact the service returned with no client and no context.

**Long-running operations**

- `LongRunningOperationResult.monitor_url` is `str | None`: `None` means "there is
  no monitor URL", which is now a real state (an operation that finished in the
  submitting round-trip) rather than an empty string. An empty string read like a
  URL to every `if result.monitor_url:` that forgot to test it.
- `MigrationServerJob.monitor()` / `monitor_async()` measure their deadline on the
  clock, so a slow `GetMigrationJobProgress` read counts against the budget: the
  loop they replaced added `interval` per iteration and never read the clock, so an
  endpoint taking longer than the whole timeout still polled indefinitely. The
  timeout raises `OperationTimeoutError` (a `TimeoutError`, so `except TimeoutError`
  is unchanged), and a job that ends `failed` is still *reported* as `"failed"`
  rather than raised — a monitor says what happened; the caller decides.
- `PollableOperation.wait()`'s `sleep` argument now defaults to `None` (the
  interruptible pause) rather than `time.sleep`, so a `cancel()` can wake it.
- `TeamsAsyncOperation.poll_for_status()` polls to completion itself (through the
  shared wait) instead of queueing a chain of `after_execute` callbacks for the
  caller's `execute_query()` to drive. The outcome is unchanged — the callback fires
  once, a failure reports rather than raises, and `create_and_wait()` /
  `clone_and_wait()` still work in one `execute_query()` — but the loop no longer
  blocks a real `time.sleep` inside a query handler, and it counts its deadline on
  the clock.

### Fixed

**Migration (client-side)**

- Verification reads each verified record once: the fresh target read behind
  `SharePointListTarget.checksum`, `read_metadata`, `read_authorship` and
  `read_permissions` is memoized for the run, so a verification pass costs one
  request per sampled item instead of up to four (a 25-item fidelity verification
  on a live list: 52 requests instead of 130, identical findings). Anything that
  writes to the target (a fidelity write, a flushed chunk, or `configure()`
  starting a new run) drops the memo.
- **A plain list is no longer routed to the server-side package.** `use_migration_api`
  now applies to document libraries only: a package can express an `SPFile` and an
  `SPFolder`, and `Manifest.xml` has no `<List>` object, so a list record had no shape
  there — `SharePointPackageTarget.write()` turned it into an `<File>` whose content
  was the record's `dict` repr (`b"{'Title': 'Write the report', 'Status': 'Active'}"`),
  with no exception and no warning. A list task now falls back to the REST adapters and
  the target says so (`… is a list, not a document library: the server-side Migration
  API carries files and folders only`), losing nothing — a record has no version
  history. The package target additionally **refuses** any item type other than `file`
  or `folder` (`ValueError`) instead of writing whatever it was handed.
- **A view keeps the columns the target list can hold.** Replaying a view named every
  captured column verbatim, so a pair whose templates disagree on a built-in column
  failed the whole replay on `Column 'LinkTitle' does not exist`; the view is now
  created with the columns that exist and the drop is returned as
  `view 'X' was created without LinkTitle: the target list has no such column`.
- **A source and target that disagree about files versus records are refused when the
  task is resolved, not at the first write.** A file share (or a document library) aimed
  at a plain list resolved fine and then failed *every* item with
  `TypeError: object is not iterable`; the other direction was worse — a list aimed at a
  document library wrote each record's `dict` repr into a file named after the item's id
  and reported `Total: 2 | Success: 2 | Errors: 0`. Both now raise a `ValueError` naming
  the two lists and what to point the task at. The adapters refuse the wrong payload
  shape as well (`SharePointListTarget` a non-dict payload,
  `SharePointLibraryTarget` a dict one), so a hand-built pair cannot corrupt a target
  either.

**Migration (Outlook)**

- Calendar and contact exports **derive their projection from the model**, and a
  cancelled event no longer slips through. `EVENT_COLUMNS`/`CONTACT_COLUMNS` were
  hand-kept `$select` lists; the calendar one named 33 columns and omitted
  `isCancelled`, which the export filters on — and `$select` answers *only* the
  columns it names (measured: a read asking for `id` alone returns a bag with `id`
  and nothing else), so a cancelled event was exported with `is_cancelled: false`
  even though `CalendarExportOptions.include_cancelled` defaults to False. Both
  constants are now `Event.select_all()`/`Contact.select_all()` —
  41 and 40 wire names, navigation properties excluded by construction — and the
  adapters' narrower dedupe reads are spelled through `wire_name()`. The envelopes
  read the model's getters (`event.subject`, `contact.display_name`) instead of
  `get_property("displayName")`, so a wire name lives in exactly one place and the
  `iCalUId`-style typo that `get_property` answers with `None` is unrepresentable.
  Live: a seeded calendar exported, imported into a second calendar, re-imported
  (3 skipped as already present) with matching digests; the same round trip for a
  two-folder contact tree.
- Calendar export records the **`iCalUId`** the service actually sends. The envelope
  read `get_property("iCalUid")` — one capital short of Graph's spelling — and
  `get_property()` answers `None` for a name it does not know, so every exported
  calendar sidecar carried `"ical_uid": null` and the `.ics` `UID` fell back to the
  tenant-local Graph event id (`UID:e1`) instead of the interoperable identifier other
  calendar clients match on. `event_envelope()` now reads the model's own
  `Event.ical_uid` getter and `EVENT_COLUMNS` selects `iCalUId`, so the sidecar and the
  `.ics` both carry the meeting identity. A tree exported by 3.3.0 keeps its fallback
  `UID` (re-export to pick up the real one); the replay itself is unchanged, since
  import matches on `graph_id` and the created event gets a fresh `iCalUId` anyway.
- Calendar export writes a **JSON-safe sidecar**: Graph's `recurrence` object is
  flattened through `to_json()` instead of being handed to `json.dumps` as a typed
  value. A recurring event's sidecar previously carried
  `"recurrence": "PatternedRecurrence(pattern=…)"` — `repr` text, produced by
  `json.dumps(..., default=str)` — which no import could replay.
- Calendar import **verifies in the source's timezone**. Exchange renders event
  times in the signed-in mailbox's own zone, so a migration into a mailbox set to a
  different zone reported every event as a content mismatch while the instants were
  identical (an event created as `09:00 Europe/Kiev` reads back as `06:00 UTC`
  unasked — measured). The verification read now asks for the item's own zone with
  `Prefer: outlook.timezone`, exposed as the new `prefer_outlook_timezone`
  (`office365.runtime.http.prefer`, works with Windows and IANA names).
- Migration fidelity reports **a product's own dimensions** instead of SharePoint's.
  `describe_fidelity` used to probe the adapter pair and always print the fourteen
  SharePoint dimensions, so a mail export forecast read
  `attachments=unsupported — list-item attachments are carried only between list
  adapters` and `views=unsupported`. An adapter can now carry a
  `fidelity_dimensions` mapping of `dimension -> (status, reason)`; the source is
  asked first, a declaration replaces the probe, and an unknown status name raises
  rather than being reported. The four Outlook directions declare theirs in
  `office365.migration.outlook.fidelity`, and a mail export now reports
  `content`/`structure`/`timestamps`/`item_state`/`attachments` — delivered — plus
  `permissions`/`versions` as unsupported. SharePoint pairs declare nothing and are
  unchanged.

### Fixed

- `ClientObject.to_json()` and `ClientValue.to_json()` (`office365.runtime`) no
  longer emit `__`-prefixed bookkeeping. A response hands back `__etag` (so
  `If-Match` can be built), `__deferred` and `__odata_type`; those describe the
  response, not the entity, and a `to_json()` that asked for a plain dict used to
  put them in a payload. A dialect's own control marker (`__metadata`) is still
  added, after the filter. `serialize_value` (`office365.runtime.converters`)
  now descends into a plain `dict`/`list`/`tuple` as well, so a payload assembled
  by hand is JSON-safe by construction rather than by `default=str` at the call
  site; a collection type that subclasses a container keeps its own `to_json`.
- `DateTimeTimeZone.parse()` (`office365.outlook.calendar`) now reads what callers
  actually pass. A `dict` in Graph's own spelling raised
  `AttributeError: 'dict' object has no attribute 'replace'`, which made
  `EventCollection.add(start={"dateTime": …, "timeZone": …})` unusable; a
  `datetime` was flattened to UTC even when it carried a zone. It accepts a
  `datetime` (an aware one keeps its own zone, an unnamed offset is converted so
  the instant survives, a naive one is read as UTC as before), a Graph dict, a
  string, or `None`, and emits the wire form Graph documents — seven fractional
  digits, no offset appended (measured: Exchange accepts both and honours a named
  zone, so an offset in `dateTime` was only a competing second zone). New
  `DateTimeTimeZone.as_datetime()` reads the wall clock back, and is deliberately
  naive: turning "W. Europe Standard Time" into an offset needs a time-zone
  database this runtime does not ship.

## [3.3.0] - 2026-10-18

Two stories: the SharePoint migration layer grew from "copy items" to a resumable,
verifiable site copy, and the runtime grew async/await, long-running operations and
a set of write/lookup primitives that the generated surface lacked.

### Breaking in 3.3.0

The public surface is additive; three modules moved, and the old import paths are
gone. Nothing else in this release changes or removes an existing API.

- `Report` calls return the new `ReportResult` (a `ClientResult` subclass, so
  `.value`, `bytes()` and `.execute_query()` behave as before) instead of
  `ClientResult[bytes]`.
- The Security API lives at `office365.security` (was
  `office365.discovery.security`).
- `TaskStatus` lives at `office365.todo.tasks.taskstatus` (was
  `office365.todo.taskstatus`).

### Added

**SharePoint migration**

- **Whole-site (same-tenant) migration.** `MigrationSession.add_site_task(...)`
  resolves a `migrate_all` task into one job per list — each with its own manifest
  and checkpoint — creating missing target containers and replaying each list's
  structure (columns, content types, views, container settings) before content is
  copied. `include_subwebs=True` mirrors the source subsite tree.
- **A run that names what it is copying.** The `migrate_site.py` console prints a
  heartbeat per list (`[ 4/24] Documents  migrating  412/1,010 (40.8%)  9.7 it/s  ETA
  1m02s`) and a closing line the moment a list finishes (`✓ [ 4/24] Documents  1,010
  copied  1m42s  9.9 it/s  2.4 MB/s`, `!` when it left failures); progress counters
  are derived per job in both serial and parallel mode (a carried-over rate and total
  no longer produce an ETA of hours), the window restarts when the stage changes, a
  heartbeat carries its `subject`, and repeated warnings print once with a count.
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
- **Best-effort batches:** `ClientRuntimeContext.collect_batch_failures()` runs a
  batch tolerantly — a rejected sub-request (denied write, validation error,
  retries exhausted) is recorded against its own query as `(query, exception)` and
  the remaining sub-requests still execute, instead of the first failure aborting
  the whole batch. Throttled sub-requests are still retried, and the default
  outside the scope is unchanged (first failure raises).
- **Lookups:** one rule for `get_by_*` (resolve one) versus `find_by_*` (return
  `None`), tolerant Graph resolvers, `ClientObject.get_or_none()`, and a bounded
  `single()`.
- **Query capabilities:** declarative `@query_capabilities(...)` with
  property-level `Prefer` injection, and a
  `Prefer: include-unknown-enum-members` helper.
- **Auth and identity:** `ClientRuntimeContext.with_auto_retry(...)` (inherited by
  clones), async token locks and `HttpxTransport` clients that follow the running
  event loop (a transport reused from a second `asyncio.run()` rebuilt its
  `AsyncClient`; a lock bound to a finished loop is replaced), a typed
  `AccessDeniedException` for 401/403, `@require_permission`
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
- Twelve duplicate model modules re-export the canonical class, and
  `ViewCollection.create`/`ensure_view` annotate `view_type` as `int | str`. (The
  three moved modules are listed under *Breaking in 3.3.0*.)

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
- Preserved runs: authorship sent its own `ValidateUpdateListItem` and the
  timestamp write then repeated the same values, so every preserved item cost two
  system updates (three with approval state). The principals are resolved and
  cached first and written **once** — with the timestamps when they are preserved,
  otherwise in a single final write before the approval step.
- Record lists: content is verified instead of reported `unverifiable`, writes
  flush and checkpoint per chunk, and `conflict_resolution=OVERWRITE` now reaches
  record targets.
- Document libraries: folders are created as folders (they were uploaded as
  files), SharePoint's own `Forms/` scaffolding and the auto-provisioned
  `SiteAssets/<web title> Notebook` are skipped rather than reported as extra
  items, folder system metadata and column values are written, approval state is
  carried, and Office Open XML documents are no longer flagged as content
  mismatches (SharePoint re-serializes them, so byte equality is unattainable).
- Warnings: structure provisioning logged each note at `warning` (one of them with
  the list name prefixed) *and* handed it to `session.warnings()`, so every note
  printed twice — once by logging's last-resort handler, once by the caller. They are
  `DEBUG` provenance now; the caller decides how to show them.
- List settings: the differing container settings (versioning, moderation,
  version limits, check-out, item-level read/write policy) are applied in one
  `$batch` instead of one request each. A change set is atomic, so a refusal falls
  back to writing them one by one — a setting the list type cannot accept is still
  its own warning and does not abort the others.
- Structure: content-type field links skip built-in and SharePoint-owned columns,
  a nameless content type no longer sends a null name, `ContentType.set_default`
  works, `reorder_fields` sends a plain JSON array, `FieldLink.field_internal_name`
  falls back to `Name`, `ContentTypeId` declares the right OData type, V3 enums
  serialize as `Edm.Int32`, and the taxonomy `TextField` round-trips.
- Structure replay: a list's content-type field links are read, added and read
  back in `$batch` rounds under `collect_batch_failures()`, so one round of three
  requests replaces the one-per-link exchange that dominated a replay (~35 requests
  for a ten-column, five-view list, ~60 % of them links). A refused column is still
  reported per column with the server's reason, and the read-back — not the
  sub-responses — decides what is linked, because a change set is atomic and one
  refusal rolls its siblings back while they answer `200`. Link order is restored
  per content type only when the target's order differs, so a re-run writes
  nothing.
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
  and list-item creates *and updates* deferred until the list's entity type is
  known (a batched hyperlink or multi-value update used to be sent unannotated and
  rejected with `A value without a type name was found`).
- Small ones: `ReportResult` raw content, `Group.created_datetime` returning `None`,
  nested OneDrive folder addressing, `ensure_folder`/`ensure_file` on a folder
  addressed by id, sharing-link expiration dates, webhook expiration format,
  `$top` sent to `directoryRoles`, sign-in timestamps as `datetime`, doubled
  apostrophes in OData literals, certificate reuse detection in the setup scripts,
  naive credential timestamps, `has_application_permissions` false negatives,
  agreement-file inheritance, the device-flow prompt, chat members right after
  creation, and `examples/onedrive/termstore/export_tree.py`.
- `SearchService.post_query` accepts `sort_list` (a list of `Sort`), the same
  argument the GET form `query` takes; it is sent in the request body as
  `SortList`. A POST that asks for no sorting sends the same body as before.

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
- **Model properties are PEP 8 names** — 628 properties across SharePoint, Graph, and security moved from camelCase to snake_case (`file.serverRelativeUrl` → `file.server_relative_url`). The OData wire keys are unchanged, so `properties["ServerRelativeUrl"]`, `get_property()`, `ensure_property()`, and `$select`/`$expand` keep working. No aliases shipped: the old names raise `AttributeError`. Migration guide: [Upgrading from 2.x](docs/upgrading.md)
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
