# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/),
and this project adheres to [Semantic Versioning](https://semver.org/).

## [Unreleased]

### Added
- **A migrated site looks like the source: its branding is carried too.** Content
  and structure were replayed but the *web* kept the target's own look — its own
  master page, its own theme, no site logo. `office365.migration.sharepoint.branding`
  now carries the properties REST accepts: `apply_web_branding(source_web,
  target_web)` reads `MasterUrl`, `CustomMasterUrl`, `SiteLogoUrl`,
  `AlternateCssUrl` and `ThemedCssFolderUrl` (one projected GET per side) and
  MERGEs only the ones that differ, so a re-run writes nothing;
  `verify_web_branding(source_web, target_web)` is the read-only half and
  `verify_site(..., branding=True)` reports it as its own dimension next to
  `settings`; `WebBranding` / `WebBrandingReport` are exported too. Three rules are
  enforced because a blind copy is wrong: every value is a path **inside the source
  site**, so it is rebased onto the target's (a master page reads back as
  `/sites/.../_catalogs/masterpage/seattle.master`, which always differs between two
  sites); every value names an **asset**, so it is written **only where the target
  resolves it** — a master page or theme folder lives in a gallery this migration
  never copies (`_catalogs/masterpage`, `_catalogs/theme` are hidden lists), and a
  logo may be the site's group image (`_api/GroupService/GetGroupImage?id=...`), a
  service endpoint with no counterpart to copy — and is otherwise reported as
  `branding: ... keeps its own MasterUrl — the target has no ...`, because a dangling
  master page would break every page on the site; and only the logo and the
  alternate CSS may be **cleared** (an unset source value writes `""`) — a blank
  master page is never written. It runs after the content, since an alternate-CSS
  URL can point into a library the run just populated. Live-verified on SharePoint
  Online: a MERGE of `SiteLogoUrl` + `AlternateCssUrl` on a web is accepted and
  reads back, writing `null` clears the logo, and a seeded source web's alternate
  CSS arrived rebased on the target with `site: ... branding: 0`.
- **Column and view formatting JSON is carried with the structure.** A migrated
  list reproduced its columns, content types, views and container settings but not
  the *formatting*: a column with a custom renderer arrived as a plain value, and a
  view with row colouring arrived undecorated. `capture_list_structure` now reads
  `Field.CustomFormatter` and `View.CustomFormatter` into `FieldDefinition` /
  `ViewDefinition`, and `provision_list_structure` replays them after the columns
  and views exist — one `MERGE` each, written only where the target's differs, so
  a re-run is a no-op. A **sealed** column accepts the `MERGE` and silently drops
  the value, so the pass reads both sides back and returns
  `column 'X' kept its own formatting: the target would not accept the formatter`
  rather than claiming success; `compare_list_structures` gained a `formatting`
  dimension so `verify_structure.py` reports a divergence too. An **SPFx field
  customizer** (`ClientSideComponentId`) is a pointer into a deployed solution and
  is reported, never copied. Live-verified: a list whose text column and default
  view both carried formatter JSON was migrated and both blobs came back
  byte-identical, with `verify_list_structure` reporting `formatting: 0`.
- **A site's custom permission levels are carried, so a grant that names one can be
  restored at all.** `preserve_permissions` replayed role assignments by *name*,
  and a name the target did not have was skipped with a warning — so a site that
  ships its own permission level lost every grant that used it, on the web and on
  every restricted list. `security.py` now reads them:
  `capture_permission_levels(web)` returns `PermissionLevel` records (name,
  description, order, decimal `BasePermissions` mask, and the service's
  `RoleTypeKind`), `apply_site_security` creates the missing **custom** ones on the
  target before it restores any assignment, and `verify_site_security` names a
  level that was not created or whose mask diverges. Two guards are deliberate: a
  **built-in** level is never created (every site has one — it is matched by
  `RoleTypeKind` too, so a localized target still lines up, and is reported rather
  than invented if genuinely absent), and an existing target level with a
  **different mask** is reported and left as-is, because rewriting what a target
  site's "Contribute" means would silently change everyone's access. Hidden levels
  ("Limited Access") are skipped — the service grants those itself. Live-verified:
  a custom level (`High=1, Low=17`) granted on a locally restricted list was
  created on the target with the identical mask, description and order, the list's
  assignment resolved to it, and both `verify_site_security` and
  `verify_list_security` came back clean.
- **A list's own permissions are replayed, so a restricted library does not arrive
  readable.** Permissions were restored at two scopes — per item by the adapters,
  and per web (site groups + web role assignments) by `apply_site_security` — which
  left a hole in the middle: a library whose permissions are *unique* (the source
  broke inheritance to restrict it) said nothing about its items, and the web scope
  is the web. It arrived inheriting the web's permissions, i.e. readable by
  everyone the site is. `security.py` gains the third scope:
  `capture_list_security(list)` (read-only; `None` when a list simply inherits),
  `apply_site_list_security(source_web, target_web, lists=None, warnings=None)` and
  `verify_list_security(source_web, target_web, lists=None)`, plus
  `ListSecurityReport` (`N list(s) carry unique permissions, M applied`).
  Application breaks the target list's inheritance **once** — only when it still
  inherits — and then adds the source's assignments through the existing principal
  resolver (default groups normalized, unknown principals warned about, never
  silently dropped), leaving every other target assignment alone: it is additive
  and idempotent, so a re-run writes nothing and never prunes. It runs **after**
  the content, because a freshly broken list is briefly unreadable to everyone but
  the writer; `migrate_site.py` calls it right after the run when
  `--preserve-permissions` is set and prints the report. Reading the flag needs
  `ensure_properties(["HasUniqueRoleAssignments"])` — a plain list read reports
  `None` even when the list is in fact unique (live-verified, as was the whole
  path: a list granting only the Visitors group `Read` arrived on the target with
  exactly that assignment and verified clean). `verify_site(..., security=True)`
  now reports it as its own `list security` dimension next to `security`, because
  one can be right while the other is wrong.
- **A migrated site opens on the copy of its source's home page.** Copying pages
  never moved a web's home page designation, so the migrated site landed on
  whatever page the target web already pointed at — the first thing a user sees.
  `pages.py` now carries it: `apply_home_page(source_web, target_web, renamed=...)`
  reads the source's `WelcomePage`, resolves it through the copy's renames (a page
  copied as `Home-1.aspx` becomes the home page), and writes the target path onto
  the target web's **root folder** — only when it differs, so a re-run writes
  nothing. `capture_home_page(web)` is the read-only half,
  `copy_site_pages` calls it at the end (recording `PageCopyReport.home_page`,
  which `summary()` reports as `home page is now …`) and a source home page that
  was not copied is *reported* — the target keeps its own home page rather than
  being pointed at a guess. `verify_page_copy` now also names a target whose home
  page is not the copy of the source's. The reason this needed its own function:
  a MERGE of `WelcomePage` **on the web is silently ignored** by the service (it
  returns success and changes nothing), while the same MERGE on
  `/_api/web/rootfolder` moves the home page — both live-verified on SharePoint
  Online, the write path proven before it was coded. `apply_home_page` and
  `capture_home_page` are exported from `office365.migration.sharepoint`.
- **Classic wiki pages are copied too, not handed off.** `pages.py` treated every
  non-modern page as transformation work, yet a wiki page's body lives in
  `WikiField`, which is readable *and* writable over REST.
  `copy_site_pages` now classifies a page as modern (a canvas), classic wiki (a
  `WikiField` body) or uncopyable (a publishing page, or a page with neither), and
  copies the classic ones through `List.create_wiki_page(name, body)` followed by a
  `WikiField`/`Title`/`Description` MERGE — the body copied **verbatim** from the
  source, because the server normalizes a body once on create (it wraps it in an
  `ExternalClass` div and entity-encodes braces) while the source value already is
  normalized, so it round-trips byte-identical. Publishing runs through
  `item.file.publish(comment)`, since a created wiki page is a draft and a
  moderation-status MERGE does not publish it. `PagePayload` gained `wiki`,
  `is_classic` and `content`; `PageCopyReport` gained `wiki` (plus `(N classic
  wiki)` in `summary()`); `PageLibrary`/`PageHandoff` distinguish
  `classic_pages`/`uncopyable_pages`, so `page_handoff_note(...,
  modern_copied=True)` now names only the pages with no copyable body;
  `capture_site_pages` and `verify_page_copy` work per page body instead of
  assuming a canvas. A copied wiki body is not rewritten, so the copy warns when
  wiki markup (internal links, wiki-embedded web parts) still addresses the source
  site. Live-verified on SharePoint Online: a 162-character body with braces and an
  internal link read back byte-identical and published to `1.0`, and a re-run's
  `verify_site` reported the same two pre-existing findings and no page drift.
- **One report answers "did this web migrate?".** A whole-site run touches a web on
  several axes, each with its own verifier, so the example called four of them by
  hand — easy to forget one, impossible to summarize. The new read-only
  `office365.migration.sharepoint.site_verify.verify_site(source_context,
  target_context, ...)` folds them into a `SiteVerificationReport` (`verify_site`
  and `SiteVerificationReport`, also exported from
  `office365.migration.sharepoint`): web `Title`/`Description`, web-scope
  structure, navigation, modern pages, site security, and — via
  `lists=[(source, target), …]` — per-list structure. Checks are opt-in so only
  what a run claimed is compared; `ok` turns False as soon as a check contradicts
  the target, while `complete` stays False when a check could not run (an access
  denied is recorded in `unverifiable`, never swallowed and never counted as a
  pass). `summary()` gives the one-line verdict with per-dimension counts,
  `issues` flattens the findings, and `to_dict()` is JSON-serializable for an
  evidence pack. `migrate_site.py` now prints that single report in place of its
  four ad-hoc verification helpers.
- **Each web's `Title` and `Description` are copied, and the settings a run
  cannot honor are no longer silent.** Replaying a list's structure never touched
  the *web* that hosts it, so a migrated site kept the target web's identity where
  people read it (site header, site card, search results).
  `office365.migration.sharepoint.site_settings` adds `apply_web_settings(source_web,
  target_web)` — one projected GET per side, then a single MERGE of only the
  properties that **differ** (so a re-run is a no-op and an unset source value
  clears the target's, since these reject `null`) — plus the read-only
  `verify_web_settings(source_web, target_web)` (one finding per property) and
  `WebSettings` / `WebSettingsReport` / `parse_site_settings_mode`, all also
  exported from `office365.migration.sharepoint`. The whole-site resolver copies
  them per web (`resolve_site_task(..., migrate_site_settings=True)`, i.e.
  `MigrationSettings.migrate_site_settings="PRESERVE_ALL_SETTINGS"`; `"NONE"` or
  `migrate_site.py --no-site-settings` leaves the target web alone, and an unknown
  mode raises instead of quietly doing nothing), through each web's own context so
  a mirrored subsite gets the source subsite's values too, and a new
  `site_settings` fidelity dimension reports `best_effort` with the reasons.
  Branding (master page, theme, `SiteLogoUrl`, alternate CSS) and the
  site-collection/regional settings stay out of scope and are named as such. The
  other half of the same problem was the **knob facade**:
  `MigrationSettings.unhonored()` now returns one ready-to-print note per setting
  whose current value asks for behavior the engine does not implement (skip-by-name
  filters, term groups, cross-tenant user mapping, multi-round, custom Azure
  storage, an unset `migration_type`, …), and a session appends them to
  `session.warnings()` once, so `skip_lists_with_name="Archive"` can no longer read
  as honored. Live-verified on SharePoint Online: the copy wrote only the differing
  property, a second run wrote nothing, `verify_web_settings` was clean afterwards
  and named the drift again once the target was restored, and a subsite round-trip
  cleared a stale `Description` back to the source's empty one.
- **Modern site pages are copied, not just reported.** A *Site Pages* library
  (`base_template` 119) holds `.aspx` pages, so the item adapters never migrated
  it and the whole-site resolver only handed it off. Modern pages are reachable
  over REST, so `resolve_site_task(..., migrate_pages=True)` (the default) now
  copies them through the rewritten
  `office365.migration.sharepoint.pages.copy_site_pages`: read the source library
  once, classify each page (modern by the
  `0x0101009D1CB255DA76424F860D91F20E6C4118` content-type prefix, classic by
  `WikiField`-only content), create the page with
  `Web.add_site_page(name, title=...)` (`POST /_api/sitepages/pages`), MERGE
  `Title`/`Description`/`CanvasContent1`/`LayoutWebpartsContent`/`BannerImageUrl`/
  `PromotedState` onto the created item, publish it with
  `Web.get_site_page_by_id(id).publish()` when the source page was published, and
  read the canvas back once to confirm it landed. Duplicates follow the SPMT
  vocabulary via `MigrationSettings.duplicate_page_behavior` — `RENAME` (default,
  `Home.aspx` → `Home-1.aspx`), `SKIP`, `OVERWRITE` — and copies are **add-only**:
  no target page is ever deleted. `verify_page_copy(source_web, target_web)`
  reconciles the copy read-only (same name *or* identical canvas counts as
  delivered, everything else is `missing`/`drifted`), and `migrate_site.py` gained
  `--no-pages` / `--duplicate-pages` plus a page line in its plan and a page
  section in its verification pass. Live-verified on SharePoint Online: a created
  page stays a draft (`OData__ModerationStatus = 3`) until the page-level publish
  runs — a MERGE of the moderation status does **not** publish it — and
  `CanvasContent1` round-trips **byte-identical** through an item MERGE (the source
  canvas is already entity-encoded), including a 10 394-character page. Also
  live-verified end to end through `migrate_site.py`: three source pages → two
  copied (one renamed around an existing page, both published, canvases intact)
  and one reported as failed because its target name was held by another user's
  check-out — the failure is recorded per page and never aborts the run. Library
  surface added: `SitePageCollection.add(name, title, page_layout_type)` (a create
  that does not name the page is rejected by the server),
  `Web.add_site_page(...)` and `Web.get_site_page_by_id(id)`. Limits stated
  plainly: **classic** pages remain a handoff (transformation, not copy), a
  serialized client-side web part still binds to the source list/library ids, page
  version history is not restored, and an empty source canvas is left alone (a new
  page already ships a default one). The page part of the handoff note now names
  only the pages a copy left behind (`page_handoff_note(..., modern_copied=True)`),
  and the `navigation` fidelity dimension moved from `handoff` to `best_effort`.
- **Web-scope structure gaps are named instead of silent.** Structure replay is
  per *list*, because that is as far as REST reaches: `FieldLinks` refuses to
  attach a column that is not reachable from the list (`Column '<name>' does not
  exist`) and the server assigns content types their own identifiers, so a *site*
  column or a *site* content type is reproduced only on the lists that use it and
  never registered at web scope. The new
  `office365.migration.sharepoint.structure.compare_web_scope_structure` (with
  `WebScopeStructure` and `web_scope_note`, also exported from
  `office365.migration.sharepoint`) reads both webs' `fields` and `content_types`
  (two projected GETs each, read-only) and reports what the target web lacks —
  *web-scope structure is not replayed: the target of <url> lacks N column(s):
  …* — while saying that a migrated list that uses one still gets a list-scoped
  copy and that the web-level definition has to be created out of band
  (CSOM/PnP). The whole-site resolver emits one note per web pair, so a subsite
  that was just created is called out too. Comparison is by internal name for
  columns and by name for content types (ids are not preserved), and
  system/hidden/framework/sealed columns are excluded so the note names real gaps
  rather than platform plumbing. It counts *definitions* — app- and
  feature-provisioned site columns appear in it too — so the note reads as "the
  target web is not a schema clone", not as a to-do list of N columns.
- **Delta re-runs: the drift a copy cannot reconcile is named.** A manifest is the
  persisted plan, but a re-run only ever reconciled *content* — an item deleted at
  the source left an orphan on the target, and a rename/move looked like a new item
  whose old target copy stayed behind (a duplicate). `MigrationJob.plan()` now
  loads the plan a previous run persisted at `manifest_path` **before** replacing
  it and diffs the two (`office365.migration.delta`: `compute_delta`,
  `DeltaReport`, `MovedItem`, all exported from `office365.migration`), exposing
  the result as `job.delta` / `session.delta()`: `added`, `missing` (planned
  before, gone now), `moved` (the same `MigrationItem.source_id` at a different
  path) and `changed` (same path, different modification time — a `skip` re-run
  leaves the target copy as it was), with `is_stale` marking a target *known* to
  differ because of a deletion or a move, and `notes()` giving one sampled,
  ready-to-print line per kind. A manifest that cannot be read degrades to a
  `delta unavailable: …` note instead of silently reading as "nothing changed".
  Detection is read-only — nothing is deleted or moved on the target, since a
  target may legitimately hold content the copy did not put there — and its
  identity limits are documented (a file's `UniqueId` is what makes a rename
  recognizable; a renamed folder has none, and a retitled list item is `changed`,
  not `moved`). `migrate_site.py` prints the notes after a run, so a re-run against
  the same `--work` folder surfaces source-side deletions/renames/edits.
- **Workflows, InfoPath forms and BCS external lists are reported as handoffs:**
  a client-side copy cannot produce any of them — a workflow is server-side state,
  an InfoPath form is an `.xsn` template plus per-list form URLs, and an external
  list is a view over a BDC model — yet the whole-site resolver only named skipped
  **page libraries**. It now names all four categories through the new
  `office365.migration.sharepoint.handoff` module
  (`detect_handoff(web, lists)` / `handoff_notes(handoff)`, also exported from
  `office365.migration.sharepoint`). Detection costs two reads per web — the web's
  `workflow_associations` and one *projected* lists read carrying each list's
  declared form URLs plus its expanded `WorkflowAssociations` — and each detector
  is best-effort: a failure becomes a note (`… detection failed for <url>: …`)
  instead of aborting resolution. InfoPath is matched on the canonical markers
  (`FormServer.aspx`, `XsnLocation=`, `.xsn`) so the stock platform forms
  (`Forms/Upload.aspx`, `Lists/X/NewForm.aspx`, `_layouts/15/aclinv.aspx`) never
  flag a normal list; a BCS list is recognised by `BaseTemplate == 600`, and is now
  **skipped** by `is_migratable_list` (creating a hollow list would be worse than a
  handoff). A `BusinessData` **column** inside a list that *is* migrated is skipped
  by the structure replay with its own warning, since replaying its schema would
  create a column that resolves nothing on the target.
- **Checked-out files are reported, not silently mis-copied:** a checked-out
  document exposes only its last *checked-in* version over REST, so the migrated
  copy was faithful to what the source returned while the author's in-progress
  edits stayed behind — and `verify()` could not notice, because it compares the
  same read on both sides. Carrying the check-out is not an option (the copy would
  be left locked by the migrating app), so the library source now detects it and
  reports it once per run: *N checked-out file(s) were copied from their last
  checked-in version (in-progress edits are not visible over REST): …* (first five
  paths, then a count). Detection rides the single item read that already supplies
  the author ids: `CheckoutUser` only projects when its sub-properties are selected
  **and** the field is expanded (a bare `$select=CheckoutUser` is rejected with
  *The query to field 'CheckoutUser' is not valid*), so the projection grows by
  `CheckoutUser/Id`/`CheckoutUser/Title` plus `$expand=CheckoutUser` and costs no
  extra request.
- **Files on an un-published (minor) version are reported too:** with minor
  versioning enabled a document can sit at `1.1` — a draft whose published `1.0`
  predecessor is what readers see. REST returns the *draft* content for it
  (live-probed: `get_content()` on a `1.1` file returns the draft), so the copy
  matches the version the source reports and the draft *state* survives — the
  approval status carries it — but the published version it supersedes does not,
  because client-side SP→SP does not restore version history. `verify()` compares
  the same read and cannot notice, so the library source reports it once per run:
  *N file(s) are on an un-published (minor) version: the draft content is copied,
  the published version it supersedes is not (version history is not preserved): …*
  (first five paths, then a count). The signal rides the recursive file listing the
  source already reads, so detection costs no extra request: a published file is
  `x.0`, a draft `x.n` with `n > 0` (`MajorVersion`/`Level` agree — on a moderated
  library `publish`+`approve` lands on `1.0`/level 1 and a minor check-in on
  `1.1`/level 2).
- **Document library folder system metadata:** a migrated folder was created with
  the migration's own `Created`/`Modified` (and its author), so every funnel's
  "last updated" date was wrong while `verify()` — which excluded folders from the
  sample — still reported `OK`. Folder items now carry their timestamps (read off
  the recursive folder listing, which already returns tz-aware datetimes) and their
  authorship, and both sides read them back from the **folder resource** rather
  than from the list item's form values, which are web-local naive strings and
  would never compare equal. Two live-probed details shape the write:
  - Folder fidelity runs in a **post-content pass**, after everything has been
    written. A folder's `Modified` follows its children — uploading a file into it,
    or creating a subfolder, resets it to now — so stamping a parent while its
    subtree is still being created silently discarded the value (found live: the
    child folder round-tripped, the parent came back as the migration time).
  - An **existing** folder is no longer skipped the way an existing file is: a
    folder holds no content to duplicate, and a resumed run has to re-apply its
    metadata, otherwise a re-verify reported every untouched folder as drifted
    (36 phantom `timestamp mismatch` issues on the lab library). Files keep the
    skip — a re-run does not re-upload or re-stamp content already there.
  After the fix a full library re-run verifies `OK | issues: 0`.
- **Document library file approval state:** a draft or rejected file migrated into a
  moderation-enabled library landed **approved**. An upload starts out approved, and
  worse, every `ValidateUpdateListItem` write on a document approves it again — so
  restoring timestamps silently published a draft. The library source now reads
  `OData__ModerationStatus`/`OData__ModerationComments` alongside the author ids it
  already reads (one extra projection, only when the library enables moderation,
  because selecting a column the list does not have fails) and the target restores
  them in a **separate, final write** — a document rejects a moderation change
  together with other item properties (*You cannot change moderation status and set
  other item properties at that same time*). Only a non-approved status is carried:
  an upload is already approved, so an approved file costs no extra round trip. A
  failed state write is a warning, never fatal. The write still moves the *list
  item's* own `Modified` (SharePoint will not combine it with anything else), so a
  draft file reports the migration time there, while its `File.TimeLastModified` —
  the value the metadata diff compares — keeps the source timestamp; `verify()` also
  compares the approval status itself, so a draft that lands approved is a
  `mismatch`, not a silent loss.
- **Document library folder column values:** a folder is a list item too — a
  document set's metadata, a managed folder's department — but the library
  adapters created folders as pure structure, so those values were lost while the
  library still verified as `OK` (`verify()` sampled items only). A
  `SharePointLibrarySource` built with its library now reads each folder's
  **writable** columns with an explicit projection (a `*` read fails on a library:
  a library has no `Attachments` column) and travels them as the folder's payload;
  a `SharePointLibraryTarget` built with its library MERGEs them onto the created
  folder's list item, `ContentTypeId` included (a `MERGE` does change a folder's
  content type). Writable means non-hidden, not underscore-prefixed, not
  read-only and not a computed type — the same rule the target applies to its
  read-back — and an empty value counts as absent on both sides. `verify()` now
  samples folders for the content check, but only when both adapters were built
  with their library, so a filesystem pair carries no folder values and reports
  nothing instead of "unverifiable". A failed value write is a warning, never
  fatal, and a pre-existing folder is not skipped, so a resumed run re-applies its
  values (see *folder system metadata* above).
- **Attribute-level column verification:** `verify_list_structure` compared columns
  by **name** only, so a column that reached the target without its policy — a lost
  `Required`/`Indexed` flag, a truncated choice list, a dropped validation formula —
  was reported as `OK`. It now also compares what each column's `SchemaXml`
  declares: type, the required/indexed/unique flags, length, format, rich text, the
  choice list, the default value, a calculated or validation formula (with brackets
  and whitespace stripped, the form its own read-back takes) and a calculated
  column's field references, reported as `column_mismatches` (and in `summary()` /
  `to_dict()`). Attributes that describe the containing site or are assigned by the
  server are ignored — the owning list id, a lookup's target list, a taxonomy
  column's hidden note list, the column id and its storage column/ordinal — because
  a faithful re-create legitimately changes them. A live whole-site run reports
  zero such differences across every library and list in the lab.
- **List container settings + approval state:** a list snapshot used to carry its
  columns, content types and views only, so the target list was recreated with
  stock policy (no versioning, no content approval, no item-level permissions).
  `capture_list_structure` now also reads the list's own settings —
  `EnableVersioning` / `MajorVersionLimit`, `EnableModeration` /
  `DraftVersionVisibility`, `EnableAttachments`, `ReadSecurity` / `WriteSecurity`,
  `ValidationFormula` / `ValidationMessage`, and on a document library
  `EnableMinorVersions` / `MajorWithMinorVersionsLimit` / `ForceCheckout` — and
  `provision_list_structure` replays them as per-property `MERGE` requests in a
  dependency order (versioning before its limits, validation after the columns
  exist), writing only the ones that differ from the target's current values (a
  limit whose versioning flag is off is not sent at all — the server rejects it).
  They are applied regardless of `on_conflict` because the item copy
  depends on them, each through its own handle so one rejection cannot leak into
  the next, and a setting the list cannot accept (a plain list rejects minor
  versions, their limit and required check-out) becomes a warning instead of a
  failure. `verify_list_structure` compares the settings too and reports a
  `settings_mismatch`; a validation formula is compared with whitespace and
  brackets stripped because the server canonicalizes it.

  Item **approval state** now travels as well: `OData__ModerationStatus` and its
  comments are record content, but every fidelity write that restores
  timestamps/authorship is a *system update*, which re-approves the item — so the
  captured state is folded into that same write (live-probed to be accepted and to
  create no new version). `item_state` is therefore a best-effort dimension for a
  list pair instead of unsupported; check-out and in-progress draft state are
  still not carried.
- **Managed Metadata (taxonomy) value migration:** a `TaxonomyFieldType` /
  `TaxonomyFieldTypeMulti` column used to be copied verbatim or dropped. The list
  adapters now carry the portable identity of each term — its `TermGuid` — and
  rebuild the payload the server accepts: a **single-value** column is written as
  a typed `SP.Taxonomy.TaxonomyFieldValue` dict, a **multi-value** column through
  its hidden note companion's `-1;#Label|guid;#...` text (a typed
  `TaxonomyFieldValueCollection` is rejected server-side). The label and the
  site-local `WssId` are deliberately not carried: the server resolves a write by
  term id, and a read may return the `WssId` string as the label. Verification
  canonicalizes both sides to a **sorted term-id list**, so a copy verifies even
  though its `WssId` differs. Structure provisioning intercepts taxonomy columns
  and recreates them with `TaxonomyField.create(...)` against the same term set
  (`SspId`/`TermSetId` read from the source schema), so the new column binds to the
  **target** web's `TaxonomyHiddenList` and gets a fresh note companion; it never
  replays the source `SchemaXml` (whose `List`/`WebId`/`TextField` name the source
  web). Same-tenant scope only: the term store itself is not migrated.
- **Page / web-part handoff:** the whole-site resolver no longer skips page
  libraries silently. The new `office365.migration.sharepoint.pages` module
  (`detect_page_handoff`, `page_handoff_note`) finds each source web's Site Pages,
  wiki and publishing page libraries, lists their pages, and counts the
  client-side web parts a modern page serializes in its canvas; the resolver
  appends the note to `session.warnings()`. At that point pages and web parts
  were still **not** migrated (page transformation belongs to external tools);
  the *Modern site pages are copied* entry above closes the modern-page part of
  that gap in the same release, leaving classic pages as the handoff. The canvas parsing is a base-library
  helper — `office365.sharepoint.publishing.pages.canvas`
  (`parse_canvas_controls`, `count_web_parts`) and `SitePage.web_part_count` — so
  any inventory that reads `CanvasContent1` can count web parts without a
  migration run.
- **Web navigation replication:** the whole-site resolver now copies each web's
  **Quick Launch** and **top navigation bar** onto the target when
  `MigrationSettings.migrate_navigation` is on (the default). The new
  `office365.migration.sharepoint.navigation` module exposes `capture_navigation`,
  `apply_navigation` and `verify_navigation`; the copy is **additive** (a source
  node already present on the target by title is left alone, its children are
  reconciled), so runs are idempotent and a target's own links are never destroyed,
  and source links are rewritten from the source web's path to the target's.
  Dynamic nodes without a URL (the *Recent* node and its computed children) and
  audience targeting are out of scope; pages and web parts were *handoff* at that
  point — modern page copy landed later in this release.
- **Web (site) security replication:** `preserve_permissions` now covers the web
  scope, not just per-item ACLs. `resolve_site_task(..., preserve_permissions=True)`
  re-creates each source web's **custom site groups** (flags + membership) and its
  **web-level role assignments** through the new
  `office365.migration.sharepoint.security` module (`capture_site_groups`,
  `apply_site_security`, `verify_site_security`). The three associated groups
  (Owners/Members/Visitors) are mapped by name onto the target web's, so a renamed
  association still lines up; their membership is left to the underlying Microsoft
  365 group and is **not** copied. Custom groups are created only when missing and
  an already-present assignment is left alone, so runs are idempotent; unresolvable
  principals are reported (never silently dropped). `migrate_site.py` runs the
  verification after a preserving run and prints any unrecovered note.
- **Lookup and Person value remapping for list migration:** a Lookup column used
  to be copied verbatim, so it pointed at the source list (and kept source item
  ids) and a Person column kept the source site-user id — both meaningless on the
  target. `SharePointListTarget` now translates each Lookup value through the
  referenced target list's `MigrationSourceId` index, and each Person value is
  carried by `SharePointListSource` as a portable **login name** and resolved with
  `web.ensure_user` to the target's own id. A Lookup column's *schema* is repointed
  at the matching target list by `rewrite_lookup_schema` (whole-site resolution is
  now two-pass: create the container lists, build the source→target id map, then
  replay structure); an unresolvable reference is skipped with a warning instead
  of creating a broken column. The verifier compares lookups by source id and
  persons by login on **both** sides, so remapped content still verifies. This
  covers single- **and** multi-value Lookup/Person columns (a multi-value column
  is selected explicitly on the source — a `*` projection omits the ids — and
  written as `{"results": [...]}` on the target); Managed Metadata values are
  still dropped (the fidelity matrix now reports `typed_values` as `best-effort`
  when both adapters advertise `supports_typed_values`).
- **Record-list item fidelity (timestamps, authorship, permissions):** the
  client-side list adapters now implement the fidelity hooks for *record lists*,
  matching what the document-library adapters already did. `preserve_timestamps`
  restores `Created`/`Modified` via `ValidateUpdateListItem` (`datesInUTC=True`),
  the new `preserve_authorship` restores `Author`/`Editor` by resolving each source
  principal through `web.ensure_user` and writing a `FieldUserValue`, and
  `preserve_permissions` copies an item's role assignments after breaking
  inheritance. `MigrationSettings` gained `preserve_authorship` and feeds it into
  every task; `MigrationJob.verify()` now also diffs authorship, over the new
  optional `DataTarget.apply_authorship(item)` / `read_authorship(item)` hooks.
  Only items with a **unique** source ACL are copied — the REST surface reports
  inherited role assignments too, so copying those would break inheritance on
  every item and duplicate the parent ACL; unresolved principals and unhonorable
  facets surface as `mismatches`/`unverifiable`, never a silent drop.
- **Opt-in subsite recursion for whole-site tasks:** `resolve_site_task` (and
  `MigrationSession.add_site_task`) gained `include_subwebs`. By default a
  whole-site task migrates only the source web's own lists but **detects its
  subsites** and reports them through `session.warnings()` (they are no longer
  dropped silently). With `include_subwebs=True` the target subsite tree is
  mirrored — each missing subsite is created with the source's template and title
  — and every subsite's lists are migrated too. Each web is addressed through its
  own authenticated `ClientContext.clone`, since a subweb's sub-collections
  otherwise resolve against the context root.
- **Structure-provisioning warnings now reach `session.warnings()`:** when a
  target content type cannot be linked to a source column, the warning the resolver
  already logged is also recorded on the target adapter (list or library), so a
  whole-site run reports what it could not reproduce instead of only writing it to
  the log. `SharePointLibraryTarget` gained the `warnings` list its siblings carry.
- **Content-type identity map for item migration:** SharePoint assigns a
  recreated list content type a fresh `StringId`, so the `ContentTypeId` carried by
  every source list item no longer exists on the target (SharePoint silently coerces
  it to the list's default content type). `ContentTypeMap`
  (`office365.migration.map`) records the source→target id, matched **by content
  type name** (the only stable key across a REST recreate). `provision_list_structure`
  populates it via the new `content_type_map=` argument, `resolve_site_task` and the
  single-list resolver thread it into `SharePointListTarget`
  (`content_type_map=`), and the item projection rewrites `ContentTypeId`
  before writing — so items land under the recreated content type instead of
  whichever one SharePoint picks by default.
- **Term-store hierarchy export/import, without the payload name clash:**
  `Store.export_tree()` / `Store.import_tree()` (and `StoreManager.export_tree()`
  / `StoreManager.import_tree()`) round-trip the whole groups → sets → terms tree
  to/from a nested list of dicts. They replace the misnamed
  `StoreManager.to_json()` / `from_json()` on the term-store *hierarchy*, since
  `to_json` / `from_json` are reserved for wire-payload (de)serialization; the old
  names remain as `DeprecationWarning` aliases.
- **Deeper post-migration validation:** `MigrationJob.verify()` now reconciles
  presence, content, and — when the run requested them — timestamps and
  permissions, using optional `read_metadata(item)` / `read_permissions(item)`
  adapter hooks. `VerificationReport` gained disjoint `extra` and `unverifiable`
  buckets plus `complete` and `to_dict()`: a requested check that could not run is
  now reported as unverifiable (so `complete` is False) instead of being silently
  skipped. `verify_list_structure(source_list, target_list)` (and
  `compare_list_structures(...)`) compare captured `ListStructure` snapshots and
  report source columns/content types/views/field links missing on the target
  (`StructureReport`).
- **Fidelity reporting and session settings plumbing:** `MigrationJob.fidelity()`
  (and `MigrationSession.fidelity()`) describe what an adapter pair can actually
  preserve — timestamps, permissions and versions — returning a `FidelityReport`
  (`preserved` / `unsupported` / `not_requested` / `notes`, with `summary()` and
  `to_dict()`). The same report carries the full **fidelity matrix**
  (`report.dimensions` / `matrix_summary()`): every modeled dimension (content,
  versions, timestamps, authorship, permissions, attachments, structure, content
  types, typed values, item state, views, navigation, sharing links) reported as
  `delivered` / `best-effort` / `unsupported` / `handoff` (a new `FidelityStatus`),
  probed from the adapters' capability attributes (`supports_versions`,
  `supports_authorship`, `supports_attachments`) and optional hooks, with a reason
  per non-delivered dimension. They are informational and never raise; the run
  still fails fast on an unhonorable flag. `MigrationSettings` gained
  `preserve_timestamps`, and a registered session now feeds its `to_options()`
  fidelity flags into every task by default (an explicit `options=` still wins), so
  `MigrationSettings(preserve_permissions=True)` is no longer silently ignored.
- **List structure capture for SharePoint migration:**
  `office365.migration.sharepoint.capture_list_structure(sp_list)` returns a
  read-only, JSON-serializable `ListStructure` snapshot of a list's **columns**
  (with `SchemaXml` prepared for `CreateFieldAsXml`), **content types** (with
  their ordered field links), and **views** (with their ordered columns), plus
  the container metadata. Built-in/system and framework columns (hidden or not
  deletable), hidden content types, and hidden/personal views are skipped. The
  snapshot round-trips through `ListStructure.to_dict()` /
  `ListStructure.from_dict(...)`, so it can be inspected, persisted, and later
  provisioned onto a target list before content is copied. It issues GET
  requests only — it never writes.
- **List structure provisioning for SharePoint migration:**
  `office365.migration.sharepoint.provision_list_structure(sp_list, structure)`
  replays a `capture_list_structure` snapshot onto a target list — creating the
  missing columns from their `SchemaXml`, the custom content types (matched by
  name), and the views — and returns the list of warnings for anything the
  server refused (currently an un-linkable content type column). It is
  idempotent: re-running with `on_conflict="skip"` (the default) changes nothing.
  Two SharePoint Online REST limits are documented and handled rather than
  hidden: a content type's `Id` cannot be preserved (the server assigns one, so
  content types are matched by name), and a fresh column cannot be attached to a
  custom content type (the write is rejected with *"Column ... does not exist"*,
  so the column is reported as a warning instead of failing the migration).
- **Whole-site (same-tenant) SharePoint migration:** `MigrationSession.add_site_task(...)`
  resolves a `MigrationTask(migrate_all=True)` into **one resumable job per list
  or document library** (each with its own manifest/checkpoint), and
  `office365.migration.sharepoint.resolvers.resolve_site_task(...)` exposes the
  underlying resolution. The registered `context` is the target; a source on a
  different site collection in the same tenant is reached through an
  authenticated `ClientContext.clone`. Document libraries use the file adapters,
  record lists use the list adapters, and hidden/infrastructure/system lists are
  skipped (`include`/`exclude` narrow the set). Target lists are created on
  demand by title with the source template type, and each list's **columns,
  content types and views are replayed** from the source before content is
  copied (pass `provision_structure=False` to only create the containers).
  Single-list task resolution (`add_task`) also classifies a source as a library
  or a record list, reaches a different source site via a clone, and replays the
  source list's structure onto the existing target list (`provision_structure=False`
  to skip; the server-side Migration API path applies structure from the package).
- **Cooperative cancellation for long-running operations:**
  `OperationPoller.cancel()` / `cancel_async()` stop an in-flight `wait()` /
  `wait_async()` by raising the new
  `OperationCancelledError` (a subclass of `OperationFailedError`, so existing
  handlers keep working). Cancellation is cooperative and **not** a rollback:
  work the service already applied remains. Pass a service-specific
  `cancel_request` to `OperationPoller` to also stop the operation server-side;
  without one, cancellation is client-side only. `OperationStatus.is_cancelled`
  and `CANCELLED_STATUSES` distinguish a cancelled terminal state from a
  failure, and `wait_async(cancel_on_task_cancel=True)` forwards an
  `asyncio.CancelledError` to the service before it propagates. `cancel()` also
  **wakes a waiting `wait()` / `wait_async()` immediately** (a blocking `wait()`
  in another thread, or a running `wait_async()` on its event loop), so even a
  long `Retry-After` does not delay cancellation.
- **Unified `upsert` primitive (idempotent create-or-reconcile):**
  - `EntityCollection.upsert(key, value, /, *, on_conflict="update", **properties)`
    is the single-entity counterpart of the keyed bulk import. It finds the
    entity with `$filter` and then creates it, or reconciles only the properties
    that differ, so an unchanged re-run queues no write. It is the portable,
    client-side path shared by Microsoft Graph and SharePoint.
  - `Entity.upsert(*, if_match=None, if_none_match=None)` is the server-side fast
    path for endpoints that implement the Microsoft Graph *upsert* pattern: one
    `PATCH` with `Prefer: create-if-missing, return=representation` against an
    alternate-key-addressed entity, with optional `If-Match` / `If-None-Match`.
    When the service does not honour `create-if-missing` it raises the new
    `office365.runtime.exceptions.UpsertNotSupported` so callers can fall back to
    the client-side verb.
  - `EntityCollection.get_by_alternate_key(key_name, key_value)` addresses an
    entity by a CSDL alternate key (`ServicePrincipalCollection.get_by_app_id`,
    `ApplicationCollection.get_by_app_id`); alternate-key metadata is now parsed
    from the CSDL into the generator's type information.
  - New `office365.runtime.http.prefer` helpers `prefer_create_if_missing()`,
    `prefer_return_representation()` and `prefer_upsert()`.
  - The record `on_conflict` vocabulary is unified to `"skip"` / `"update"`
    across the single-entity and bulk paths (`"upsert"` is retired).
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
- **`ViewCollection.create` / `ensure_view` annotate `view_type` as `int | str`.**
  The parameter always accepted either an integer `ViewTypeKind` or its name (the
  docstring said so, and the collection normalizes both), but the annotation said
  `int` only. Passing a view's own `view_type` (a read returns the name) is now
  type-correct; no runtime behaviour changed.
- **`verify()` reports are more precise:** unexpected target items no longer
  masquerade as content `mismatches` — they are reported in the new
  `VerificationReport.extra` bucket, which (like `missing`) makes `ok` False.
  `summary()` now reports `MISMATCH`, `PARTIAL` (nothing contradicted, but some
  requested check was unverifiable), or `OK`. The shared report is used by the
  data pipeline too, whose callers are unaffected (the new fields default empty).
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
- **Duplicate model modules now re-export the canonical class.** Twelve modules
  declared a *second* class for an OData type that another module already
  models — leftovers of hand-written modules that the generator later placed
  elsewhere. Both files stayed importable, so the class you got depended on the
  import path, and the generator reported both modules as claimants of the same
  type (the same hazard that had `--force` writing `SP.Field` members into a
  hand-written file). Each duplicate now re-exports the canonical class, so every
  existing import keeps working and there is one class per type:
  `office365.communications.onlinemeetings.chatmode`,
  `office365.outlook.attachment_info`, `office365.partners.partnertenanttype`,
  `office365.reports.partners`,
  `office365.onedrive.operations.public_inner_error`,
  `office365.common.task_file_attachment`,
  `office365.onedrive.wellknown_list_name`,
  `office365.teams.operations.asyncoperationtype`,
  `office365.directory.permissions.identity_set`,
  `office365.security.attribute_mapping`, `office365.todo.attachments.type`
  (`microsoft.graph.attachmentType` additionally gained `unknownFutureValue`) and
  `office365.externalconnectors.content_category` (which now models the connector
  enum, see below). The generator's duplicate-name report for Graph went from 14
  types to 1 — `ConversationMember` deliberately writes as
  `AadUserConversationMember`, so the shared claim is documented in place.
- **`TaskStatus` moved to `office365.todo.tasks.taskstatus`** (was
  `office365.intune.print.taskstatus`). The enum models the Microsoft To Do task
  status and is only used by `TodoTask`, so it now sits next to its consumer.
  Update imports accordingly.

### Fixed
- **A provisioned library no longer reports field links it could never have.** A
  content type's `FieldLinks` also name built-in and SharePoint-owned columns
  (`Title`, `FileLeafRef`, and the framework columns SharePoint provisions for
  itself — `MediaServiceMetadata`, `MetaInfo`, `_VirusStatus`, …). Those are hidden
  or non-deletable, so structure provisioning neither recreates nor links them
  (linking one is a guaranteed server error), yet the structure comparison counted
  them as missing: every full-site `verify_structure` run ended with
  `[MISMATCH] Site Assets: field links: 6` for the six `MediaService*` columns
  alone. `capture_list_structure` now keeps a content type's links only for columns
  the snapshot can actually recreate (the same set `_reconcile_field_links` links),
  logging the dropped names at debug level, so the comparison measures what the
  migration can deliver. Live-verified on SharePoint Online: the full-site
  `--all` run that previously ended in that mismatch is now `[OK]` for every list,
  *Site Assets* included.
- **An item's ACL could be applied blind: empty, broken twice, or misreported.**
  `apply_permissions` broke inheritance first and only then resolved what to grant,
  on both the record-list and the document-library target. A source ACL whose
  principals all fail to resolve on the target (a cross-tenant account, an app
  principal, a renamed group) therefore ended up as an item with inheritance
  broken and **nobody granted** — less accessible than leaving it alone; and
  because the `HasUniqueRoleAssignments` flag is *not* part of a plain entity
  read, an item loaded before its ACL was written kept a stale `False`, so a
  re-run broke inheritance on an item that was already unique and the run's own
  verification read `[]` back and reported a permission **mismatch** for an ACL
  that had in fact landed. Both targets now share
  `_replay_role_assignments(...)`, which resolves every principal and role
  *before* writing anything, warns about each role the target does not have,
  breaks inheritance only when the item still inherits **and** at least one
  assignment resolved, and otherwise leaves the item inheriting with
  `permissions for '…' were not restored: no assignment could be resolved on the
  target …` — add-only and idempotent either way, so a re-run adds only what is
  missing and never removes a grant the source does not carry.
  `_has_unique_role_assignments(securable, refresh=True)` re-reads that flag with
  a projection (restoring the object's query options afterwards) instead of
  trusting the cached copy. Live-verified on SharePoint Online: a record list with
  one restricted item and one inheriting item, plus a library with a restricted
  folder and an inheriting one, migrated with
  `list:AclList: OK … issues: 0` / `library:…/AclLib: OK … issues: 0`, the target
  reading back exactly the source's assignments (normalized members) and the
  inheriting items still inheriting.
- **Generated Graph enums sent their CSDL ordinal instead of the member name.**
  The generator renders a CSDL enum member as `name = "<Value>"`, so a large part
  of the Graph model carries ordinals rather than wire values — `TaskStatus`
  is `notStarted = "0" … completed = "2"`. `serialize_value` returned a string
  value verbatim, so a write payload contained `"2"` where Graph expects
  `"completed"` (SharePoint's `Edm.Int32` enums were already handled by the
  int branch). A digit-only string value now falls back to the member name, which
  is what the OData V4 branch always intended (reads were unaffected: `parse_enum`
  already falls back to a name lookup). Verified by unit test rather than against
  the tenant — the lab app is not granted `Tasks.ReadWrite.All`, so the live
  To Do round-trip was not available.
- **Two models claimed the wrong OData type name.** `office365.security.security.Security`
  returned `microsoft.graph.security.alert` (a copy-paste from `Alert`), so the
  root security entity serialized with `Alert`'s `@odata.type`;
  `office365.externalconnectors.content_category.ContentCategory` claimed the
  base `microsoft.graph.ContentCategory` while modelling the connector enum that
  Graph names `microsoft.graph.externalConnectors.contentCategory`, which made
  `SearchConnection.content_category` default to `ContentCategory.none` — a member
  that only the *base* enum has. The connector enum now matches the service
  metadata (`uncategorized` … `unknownFutureValue`) and the default is
  `uncategorized`; the lifecycle-workflow enum keeps the base name.
- **A PUID's `0x` prefix (or stray whitespace) reached `UserGroup.xml` verbatim.**
  `is_puid` accepted `0x100320006514b083` as a legitimate PUID — the digits are
  what the Migration API's `SystemId` carries, but the prefix is not: the service
  parses the attribute as a number, so a prefixed or space-padded value was
  validated and then written through unchanged. `office365.migration.base` now
  exposes `normalize_puid`, which returns the 16 hex digits (prefix and whitespace
  stripped, case preserved) or `None`; `is_puid` is defined in terms of it, and it
  is applied wherever a PUID enters the payload — `PackageBuilder.add_user` (which
  still rejects a GUID or a claims login) and `UserGroupMap.to_xml` as the last
  chokepoint before the service sees the value, plus both SharePoint adapters'
  principal resolution, so `Principal.system_id` is canonical throughout.
- **The model generator could write into hand-written files.** Two classes that
  are not model types used to claim an OData name through the
  `<namespace>.<ClassName>` fallback and shadow the real class, so `--force`
  injected generated members into them: the CAML DSL `Field` in
  `office365/sharepoint/listitems/caml/expressions.py` claimed `SP.Field` (281
  lines of `SP.Field` accessors, caught by pyright), and the migration package
  `@dataclass Package` in `office365/migration/package/builder.py` claimed
  `microsoft.graph.Package` (a stray `type` field and an `entity_type_name`
  property, committed by accident). A class with **no base classes** is now never
  a resolution candidate unless it *declares* `entity_type_name` — every generated
  model class inherits `Entity`/`ClientValue`/`Enum`/… — so both collisions are
  gone structurally. The accidental `Package.type` / `Package.entity_type_name`
  members are removed (never released, never used).
- **A forced regeneration re-declared inherited dataclass fields.** The
  hand-written `graph.keyCredential` / `graph.passwordCredential` dataclasses
  inherit `displayName` / `keyId` / `startDateTime` / `endDateTime` from
  `Credential`, yet their CSDL type is a *root* complex type that declares those
  four properties itself, so `--force` appended them to each subclass — shadowing
  the inherited values with `None` defaults. The reserved-member set is now
  snake-cased before it is keyed: the on-disk spelling (`displayName`) and the
  CSDL spelling (`display_name`) differ, so an inherited field reserved nothing
  and was re-declared. A forced regeneration of both models now plans **0 created,
  0 updated** (it planned 2 updates before).
- **Hyperlink column values were dropped on migration.** A `URL` column reads as a
  `{"Url": ..., "Description": ...}` object — not a scalar — so the source
  projection dropped it with the same "skipped non-scalar column" warning and
  every migrated item lost its links. The source now carries that object for a
  column whose type is `URL` (live-probed: a create *and* a `MERGE` update accept
  the plain object, and it reads back in the same shape, while a bare string is
  accepted but makes every later read of the column fail), and the checksum hashes
  scalar-only value objects so a lost or edited link is a real `mismatch`. Value
  objects of any other type (image/thumbnail, geolocation) are still dropped with
  the warning rather than sent in a shape the server may reject.
- **Multi-choice column values were lost on migration.** A `MultiChoice` column
  read back as a positional mapping (`{0: "red", 1: "green"}`) — neither a scalar
  nor a column the adapters knew how to remap — so the source projection dropped
  it with a "skipped non-scalar column" warning and every migrated item lost its
  selections. Worse, verification could not see the loss: the checksum only hashes
  scalars and lists, so a positional mapping was excluded on **both** sides. The
  source now records a multi-choice cell as a bare list (dropping an empty
  selection so the column reads back empty rather than as an empty collection) and
  the target wraps it as `{"results": [...]}` for the create — live-verified to be
  accepted on create *and* on a `MERGE` update. The read-back mapping is
  canonicalized to the same bare list before hashing, so a lost or changed
  selection is a real `mismatch` instead of an invisible drop. A column is treated
  as multi-value only when it reports `TypeAsString == "MultiChoice"`: a column
  created from `Type="Choice" Mult="TRUE"` keeps that `Mult` flag in its schema
  but stores a **single** value in one `nvarchar` slot (live-probed: a scalar write
  round-trips, an array is rejected), so the schema flag is deliberately ignored.
- **A multi-value Lookup/Person column spelled `Type="Lookup" Mult="TRUE"` was
  migrated as if it were single-value.** SharePoint keeps the declared spelling and
  reports `TypeAsString` as `Lookup`/`User`, so classifying a column by its type
  string alone treated its `<name>Id` collection as a single id: a
  `MultiDeptId = [2, 3]` never reached the target, a multi-person kept source
  site-user ids, and verification agreed with the wrong result because the column
  had been dropped before the checksum. Classification now also consults
  `AllowMultipleValues` (live-verified), which is the only reliable signal. The
  source column read also selects that property explicitly: a preceding structure
  capture leaves a narrower `$select` on the shared `List.fields` collection, and a
  field payload without `AllowMultipleValues` silently re-broke the detection.
- **Structure provisioning skipped a nameless content type instead of sending a
  null name.** `provision_list_structure` handed the captured name straight to
  `ContentTypeCollection.ensure`, so a capture without one would have posted a
  null `Name` and been rejected by the server. Nameless content types are now left
  out (like the base content types it already filters), and only named ones are
  provisioned and reconciled.
- **Taxonomy base-library fixes:** `TaxonomyField.create` no longer emits the
  containing list's id in the column schema. A `List=` attribute made SharePoint
  bind `LookupList` to the list itself, after which every taxonomy read failed with
  `SPFieldValidationException` ("the given guid does not exist in the term store");
  the schema now omits `List` and lets the server bind the web's
  `TaxonomyHiddenList`. `TaxonomyFieldValueCollection` accepts both the
  one-argument list form and the legacy `(value, values)` form, and serializes to
  the note text the server accepts. Setting a multi-value taxonomy value on a list
  item now resolves the hidden note companion through the column's `TextField` id
  (instead of guessing `{name}_0`) and writes it synchronously, so the value is
  saved. **Breaking:** `TaxonomyFieldCreateXmlParameters.ListId` was removed — it
  was never needed and produced the broken schema.
- **Verifying an empty migrated list:** `SharePointListTarget.list_paths()` now
  creates its source-id marker before reading the index. An empty source list never
  queues a write, so the marker column was not created during migration and
  verification failed with "The field or property 'MigrationSourceId' does not
  exist"; it now reports zero paths cleanly.
- **A list item with an empty multi-value Lookup/Person column reported a
  content mismatch on verification.** The source drops an empty multi-value column
  while the target reads the column back as `None`, and the content checksum
  treated an absent key and an explicit `None` as different. A null column is now
  normalized to "absent" in the checksum, so an empty multi-value column verifies
  as equal, while a value on one side and null on the other is still a mismatch.
- **Bulk list-item creates now adopt the list's entity type annotation.** The
  `add_item` path resolved `ListItemEntityTypeFullName` (so a collection-valued
  column such as a multi-lookup/person serializes with its expected type), but
  `ListItemCollection.queue_records` / `from_records` did not, so a bulk create
  carrying a multi-value column was rejected with `InvalidClientQueryException`.
  `_import_records` now resolves the annotation once (before the creates) and
  stamps every queued item.
- **`ListItem.set_property` persisted multi-value Lookup values but silently
  dropped multi-value Person values.** It special-cased `FieldMultiLookupValue`
  when deriving the writable `<name>Id` column (and the transient `<name>`) but not
  `FieldMultiUserValue`, so `item.set_property("Owners", FieldMultiUserValue([...]))`
  looked successful yet wrote nothing (the existing integration test only asserted
  the non-persisted property map, which masked it). Both value types are handled
  alike now.
- **Record fidelity writes now use a system update, so they no longer create
  versions.** `ValidateUpdateListItem` was called with
  `bNewDocumentUpdate=False`, which creates a new version for every
  `Created`/`Modified`/`Author`/`Editor` write — a migrated record arrived at
  `1.0` and left at `2.0`/`3.0`. It is now called with
  `bNewDocumentUpdate=True` (CSOM `ListItem.UpdateOverwriteVersion`), which
  overwrites those fields *without* a version bump (live-probed: `False` -> `2.0`,
  `True` -> `1.0`). An item gains at most one version, and only for a genuinely
  unique ACL, since breaking role inheritance is itself a change.
- **List-item attachments are migrated content-only and no longer noise up the
  fidelity report.** SharePoint exposes no client-side path to set an
  attachment's own system metadata (an attachment has no backing list item to
  `ValidateUpdateListItem`), so timestamps/authorship/permissions cannot be
  restored for it. The timestamp/authorship/permission diffs now exclude
  attachments and report the gap once as `unverifiable` instead of a misleading
  per-item `(no metadata)`; attachment presence and md5 content are still checked.
- **List and library fidelity writes now land truthfully.** A live
  same-tenant run (`team_in` -> `team_out`) with
  `--preserve-timestamps/--preserve-authorship/--preserve-permissions` surfaced
  several defects, all fixed: fidelity facets are applied in order
  (permissions, then authorship, then timestamps) so the last write owns the
  fields SharePoint auto-bumps, and the pending `Author`/`Editor` are folded into
  the timestamp write (a `ValidateUpdateListItem` call with only
  `Created`/`Modified` silently reset `Editor` to the caller). System/app
  principals are skipped in authorship because a rejected field rolls the whole
  `ValidateUpdateListItem` batch back even though the response reports
  `HasException=False` per field; rejected fields are now surfaced as warnings,
  and the site's default Owners/Members/Visitors groups are normalized to a stable
  token so the permission diff compares like with like across sites.
- **Timestamps now restore the exact instant on both list and document items.**
  Live probes showed list items honor ISO `...Z` as UTC while document items
  ignore `datesInUTC` and reject `Z`, parsing the space form as *web-local* (a
  `--preserve` of a document then shifted the instant by the web's offset). The
  canonical value stays UTC; the library target converts it to web-local at write
  time through the server's `RegionalSettings.TimeZone.UTCToLocalTime`, so DST is
  handled server-side. To make that function call work, `ODataPathBuilder` now
  serializes a `datetime` argument as an OData v3 `datetime'...'` literal (and a
  `date` as `date'...'`); it previously fell through to `quote(str(value))` and
  produced an invalid path.
- **Verification read stale properties after a fidelity write.** The library
  target's `read_authorship` reused the securable snapshot taken before the write,
  so it reported no author/editor and flagged a false authorship mismatch. The
  library target now re-reads the written item before diffing, matching what the
  list target already did.
- **`is_puid` rejected legitimate users whose PUID contains hex letters.**
  SharePoint renders `UserInfo.UserId.NameId` as a 16-character hex string, so a
  decimal-only check dropped e.g. user 7 (`100320006514b083`) from the
  server-side user map and logged a misleading skip. It now accepts the hex form.
- **Record-list content is now verified instead of reported `unverifiable`.**
  The list target's `checksum` used to return an empty hash, so live runs showed
  `unverifiable: content` for every record. The source and target now hash the
  item's scalar content columns with the same stable, order-independent
  projection (server-assigned identity, separately-checked timestamps/authorship/
  permissions, the remapped `ContentTypeId`, version bookkeeping and navigation
  properties are excluded), so a field-value difference is a real `mismatch`.
  Navigation properties (`ParentList`) are dropped silently; only typed columns
  that cannot be remapped keep a warning.
- **Record-list writes are flushed (and checkpointed) per chunk.**
  `SharePointListTarget` queues each item's create until a flush, so a large list
  migration at `concurrency=1` accumulated every entity and recorded the item as
  `DONE` *before* the write was ever sent — memory grew unbounded and the
  checkpoint ran ahead of the durable write. It now declares
  `deferred_writes = True`, so the runner takes the chunked (write-then-record)
  path even with a single worker, plus an incremental identity index (`Id gt
  <max>`) so idempotency checks don't rebuild the whole index on every chunk.
- **Content-type field links no longer attempt built-in columns:** a captured
  content type links every built-in and SharePoint-owned column (`Title`,
  `FileLeafRef`, framework columns, ...) that `capture_list_structure` deliberately
  does not recreate, so reconciling them produced one guaranteed `Column '<name>'
  does not exist` failure each. `provision_list_structure` now links only columns it
  captured (or that are already linked), leaving the rest to the target list's own
  defaults, and reorders exactly the links it owns.
- **Site Assets reported a phantom "extra" item (and copied site branding).**
  Every modern site auto-provisions ``SiteAssets/<web title> Notebook``, which
  SharePoint recreates on the target under the *target* web's name — so a migrated
  Site Assets always looked like it had one extra folder and one missing one. The
  notebook folder and the ``__siteIcon__.png`` site icon (per-site branding) are
  now treated as Site Assets scaffolding and skipped on both sides, like
  ``Forms/`` / ``desktop.ini``. *Live-validated: Site Assets `OK`, 0 items, 0 extra.*
- **Verification flagged valid Office documents as content mismatches.**
  SharePoint re-serializes Office Open XML documents on upload — document property
  promotion/demotion rewrites ``docProps/`` / ``customXml/`` and adds ``[trash]/``
  parts — so the md5 of a client-side REST round-trip is never byte-stable
  (`Financial Sample.xlsx` grew 83418 → 85056 bytes and changed on every upload,
  while the same bytes stored as ``.zip``/``.bin`` round-tripped exactly). The
  validator now falls back to a canonical package comparison for Office files,
  comparing every part **except** those SharePoint owns: an equivalent document is
  reported as an ``unverifiable`` caveat instead of a false ``content mismatch``,
  while a difference in any other part is still a real mismatch.
  `SharePointLibraryTarget` gained a `read(item)` hook to support this.
  *Live-validated: `Documents` 151/151, 0 issues, 1 honest Office caveat.*
- **Document-library migration dropped every folder.** The library source plans
  folders as first-class items (``dest_path`` ending in ``/``), but
  ``SharePointLibraryTarget`` treated every item as a file upload — so each
  folder was sent as a file named after the folder and rejected with
  ``System.ArgumentException: parameters.Url``. On the ``Documents`` library of
  the acceptance site that failed all 62 folders (`errors=62`). The target now
  creates folder items (deduplicated, one round-trip via `ensure_folders`),
  recognizes them in `exists`/`checksum`/`modified`/`read_metadata`, and
  `list_paths()` enumerates folders (with the same trailing slash and scaffolding
  filter as the source) so verification pairs them instead of reporting them
  missing. *Live-validated: `Documents` 151/151 items, `OK` on apply and on an
  idempotent re-run.*
- **`ClientContext.clone(url)` sent every request to the original site.** A clone
  correctly stored the new URL on the context, but `reuse()` swaps in the source's
  shared `AuthenticationContext` (to keep one token cache and transport), and
  `SharePointRequest.service_root_url` derived routing from that auth context's
  `url` — so a clone silently talked to the source site. `base_url` /
  `service_root_url` now use the request's own base URL (matching
  `ODataRequest` and the batch requests), while auth stays shared. This broke the
  whole-site same-tenant resolver (`resolve_site_task` cloned the target context
  to the source URL, yet listed the target's own lists) and any cross-site read.
  *Live-validated.*
- **`Manifest.save()` / `Checkpoint.save()` crashed on a fresh run directory.**
  The manifest was written with a plain `open()` and the checkpoint's atomic
  writer did not create the parent directory, so
  `session.add_site_task(..., manifest_dir=work/"manifests")` failed with
  `FileNotFoundError` on the first `plan()` — the default `migrate_site.py
  --work` path. `atomic_write_json` now creates missing parent directories, and
  `Manifest.save` uses it (same crash-safe write-then-rename as the checkpoint).
- **List-item create failed on typed values.** A full list read also returns
  navigation properties (`ParentList`) and typed values (`PredecessorsId`,
  `AssignedTo`, ...) whose JSON objects carry no `__metadata.type` here, so the
  create batch was rejected with `InvalidClientQueryException: A value without a
  type name was found`. Typed-value remapping is not supported yet, so the
  projection now drops non-scalar values (keeping `str`/`int`/`float`/`bool`/
  `None`) and reports the skipped columns via `warnings`, instead of failing the
  whole list migration.
- **Verification reported migrated libraries as having "extra" content.** The
  source projection skips SharePoint-owned scaffolding (`Forms/`,
  `desktop.ini`) but `SharePointLibraryTarget.list_paths()` did not, so every
  migrated library came back as a false `MISMATCH` with the target's own system
  files counted as extras. The target now skips the same scaffolding.
- **Authorship and ACLs now take effect on the server-side package path.** The
  library source resolves each item's `Author`/`ModifiedBy` and role assignments
  (`PermissionEntry` gained `system_id`/`display_name`/`email`/`role_masks`, and
  `MigrationItem` gained `author`/`editor` principals), the runner persists them
  through the manifest, and `SharePointPackageTarget` emits them: authors become
  `UserGroup.xml` principals (matched by the integer id) and, with
  `preserve_permissions=True`, each item's ACL becomes a `DeploymentRoles` role +
  a `DeploymentRoleAssignments` grant. Roles use a fresh non-system id and a
  decimal `PermMask` (the service matches by `Title`, so no duplicate level is
  created); grants target the file (`object_type="2"`). ACLs are best-effort
  same-tenant and cover **resolved users only** — groups and principals without a
  PUID are skipped and reported via `warnings`. `PackageBuilder.add_role` now
  rejects a non-decimal `perm_mask`, and the builder exposes `object_id(path)` /
  `item_url(path)` / `set_include_security(value)`.
- **Version history was not carried through `MigrationJob`:** the server-side
  package target could build `<Versions>`, but the runner never fed it any. The
  runner now reads `source.read_version_history(item)` into each item when the
  target advertises `supports_versions` (the package target does) and
  `SharePointPackageTarget` passes labels/versions to `PackageBuilder.add_file`,
  so a `SharePointLibrarySource` → `SharePointPackageTarget` job preserves file
  version history end-to-end. `describe_fidelity` / `_assert_fidelity_supported`
  now honor `preserve_versions` for that pair instead of rejecting it.
  *Live-validated* (3-version file imported as current 3.0 + history 1.0/2.0).
- **Document-library migration tried to copy SharePoint's own `Forms/`
  scaffolding:** `SharePointLibrarySource` enumerated the library's built-in
  `Forms/` folder (`AllItems.aspx`, `EditForm.aspx`, `template.dotx`, ...), which
  collides on a fresh target and fails the whole server-side job
  (`A file with the name .../Forms/AllItems.aspx already exists`). The source now
  skips the `Forms/` tree and `desktop.ini`, mirroring SPMT.
- **Server-side package timestamps were emitted as invalid XML dateTime:** the
  manifest serializer rendered `datetime`/`date` attributes with `str(value)`,
  producing the space-separated `2026-10-15 06:57:05+00:00` form that the
  Migration API rejects with `JobFatalError ... 'TimeCreated' attribute is invalid
  ... XmlSchemaValidationException`. Date attributes are now serialized as XSD
  `dateTime` in UTC (``YYYY-MM-DDTHH:MM:SSZ``). *Live-validated.*
- **Server-side file versions were lost:** `PackageBuilder.add_file(versions=[...])`
  emitted only the older versions inside `<Versions>` and relied on the outer
  `<File>` blob for the current one. The Migration API builds history from
  `<Versions>` and promotes its **last** entry to current — so a 3-version file
  imported as 1.0/2.0 only and the newest content was dropped. The builder now
  appends the current version last. *Live-validated.*
- **Server-side migration silently skipped structure replay:** resolving a
  single-list task with `MigrationSettings(use_migration_api=True)` skipped
  `provision_list_structure` on the assumption the package applied the structure,
  but the package emits no columns/content types/views — so a library with custom
  columns lost them with no warning. The source list's structure is now captured
  and replayed over REST for both engines (still toggleable with
  `provision_structure=False`).
- **SharePoint list-item migration lost every field value and every attachment:**
  `SharePointListSource` projected the collection's literal `select` (`["*", ...]`)
  instead of the loaded fields, so records reached the target empty while the run
  still reported success; attachments were dropped with no warning. The source now
  projects every readable field (excluding the `AttachmentFiles` navigation),
  captures attachments as separate manifest items, and the target uploads each
  attachment to its parent once the records are flushed. To pair the two sides for
  verification — and make the default `SKIP` policy idempotent on re-runs — the
  target stamps each item with a `MigrationSourceId` marker column (opt out with
  `identity_field=None`). List-item record content checksums stay `unverifiable`
  (honest), while attachments are md5-checked, and `MigrationSession.warnings()`
  now surfaces adapter-level skips.
- **Errors are no longer silently swallowed by a stale error handler:** the
  request `onError` dispatch treated *any* registered handler as "handled", so a
  scoped handler left behind by an earlier query hid unrelated later failures
  (for example a rejected content type field link was returned as a stub object
  as if it had succeeded). A failure is now swallowed only when a handler's
  `condition` matches; otherwise it is re-raised.
- **`ContentType.reorder_fields` / `FieldLinkCollection.reorder`:** the
  `fieldNames` / `internalNames` payloads are now sent as a plain JSON array.
  They were previously wrapped as an OData `Collection(Edm.String)` object, which
  the server rejected with *"...a node of type 'StartObject' was read ... however,
  a 'StartArray' node was expected."*
- **Migration checkpoints are now crash-safe:** `office365.migration.checkpoint.Checkpoint.save`
  wrote the JSON file in place, so a crash mid-write left a truncated file the
  next run could not resume from. It now uses the same atomic
  (temp file → `fsync` → rename) write as the streaming-import checkpoint, via
  the new `office365.runtime.persistence.atomic_write_json` / `read_json` helpers
  (also adopted by `ImportCheckpoint`).
- **`ContentType.set_default`:** now works. It previously set a `Default`
  property that SharePoint's REST API does not expose on `SP.ContentType` (the
  server rejected the update with *"The property 'Default' does not exist on
  type 'SP.ContentType'"*). The default content type is actually the first entry
  of the list root folder's `UniqueContentTypeOrder`, so `set_default()` now
  loads the folder's current order and rewrites it (target first; `False` moves
  it to the end). Only meaningful for a list-scoped content type
  (`list.content_types`).
- **`ContentTypeId` OData type name:** hand-written `ContentTypeId` now reports
  `SP.ContentTypeId`, so serializing a `Collection(SP.ContentTypeId)` (for
  example a root folder's `UniqueContentTypeOrder`) emits the correct
  `__metadata` type instead of a `Collection(None)` the server rejects.
- **OData V3 enum serialization:** SharePoint enums are `Edm.Int32` and now
  serialize as their numeric value instead of their member name (which the
  server rejected with *"Cannot convert a primitive value to the expected type
  'Edm.Int32'"*). Graph/OData V4 enums keep serializing as the member name.
- **Taxonomy field `TextField` deserialization:** `TaxonomyField.text_field_id`
  is now bound to the OData `TextField` property, so listing web/list fields no
  longer trips the computed `text_field` getter's assertion
  (`assert text_field_id is not None`).
- **`FieldLink.field_internal_name` on read:** SharePoint's REST API returns the
  linked field's internal name in `Name` and leaves `FieldInternalName` (a
  creation-time property) empty, so the property now falls back to `Name`.
  Examples that filter or compare field links no longer see `None` for every
  link.
- **Migration conflict policy reaches record targets:**
  `MigrationOptions(conflict_resolution=OVERWRITE)` previously did not overwrite
  keyed list records — `SharePointListTarget` kept its own `on_conflict="skip"`
  default. The runner now calls an optional `DataTarget.configure(options)` hook
  before the first write, and `SharePointListTarget` maps `OVERWRITE` →
  `on_conflict="update"` (anything else → `"skip"`); an explicit
  `on_conflict=` still wins. `RENAME` has no record-level meaning (records are
  keyed, not pathed) and maps to `"skip"`.
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
- **`examples/onedrive/termstore/export_tree.py` crashed:** the script called
  `Store.to_json()` and then `.execute_query()`, but `Store` inherits the payload
  `ClientObject.to_json()`, which returns a plain `dict`, so the example raised
  `AttributeError`. It now uses `Store.export_tree()` / `import_tree()`, matching
  the documented README snippet.

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
- **`MigrationMode`:** the unused `office365.migration.base.MigrationMode` enum
  is gone. It duplicated the generated `office365.teams.migration_mode.MigrationMode`,
  carried a bogus `microsoft.graph.MigrationMode` type name, and no code used it —
  the FULL/INCREMENTAL choice is `MigrationOptions.incremental` and the UPSERT
  behavior is `MigrationOptions.conflict_resolution`. This is a breaking import
  change.
- **Three stale duplicate model modules:** `office365.onenote.operations.operation`
  (whose `Operation` claimed `microsoft.graph.partners.billing.Operation` — the
  wrong type entirely, and the second claimer of `microsoft.graph.Operation`),
  `office365.sharepoint.customactions.action` (a second `UserCustomAction`, next
  to the canonical `office365.sharepoint.usercustomactions.action` — the generator
  had been updating *this* copy, so the canonical class was frozen as the thin
  one) and
  `office365.sharepoint.contentcenter.machinelearning.publications.result`
  (whose `SPMachineLearningPublicationsResult` claimed the *singular*
  `…SPMachineLearningPublicationResult` name, i.e. it masqueraded as its own
  element type). Each is an old-layout leftover: a forced regeneration of both
  models now plans **0 created, 0 updated**, and `--report-duplicates` no longer
  lists `microsoft.graph.Operation`. Replacement imports are one line —
  `office365.common.operation`, `office365.sharepoint.usercustomactions.action`
  and `office365.sharepoint.contentcenter.sp_machine_learning_publications_result`.
  The canonical `UserCustomAction` gained the 20 properties the generator had been
  writing into the duplicate (including `id`, `rights`, `description_resource` and
  `title_resource`), and `OnenoteOperation` now derives from the real
  `microsoft.graph.Operation`, so its `status` is an `OperationStatus`. This is a
  breaking import change.

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
- **Migration path guidance and honest server-side limits:** `docs/migration.md`
  gained a "Client-side vs server-side" section that compares the two engines
  (content, versions, permissions, structure, Azure, verification) and says when
  to pick each. The builder emits no columns/content types/views (provision those
  over REST first), and the examples migration README matches.

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
