# Step 3 — Create a migration task

Run the migration itself: filesystem ↔ library, list export, parallel sessions,
and server-side packages. Part of [Migration](../README.md), which walks through
the job model, incremental re-runs and the server-side five-step flow.

| What | File | Notes |
|------|------|-------|
| Filesystem → filesystem | [`migrate_files.py`](./migrate_files.py) | Foundational `MigrationJob` |
| Export a list to JSON | [`export_list.py`](./export_list.py) | "From SharePoint" |
| Library ↔ local (bidirectional) | [`migrate_library.py`](./migrate_library.py) | `--import`, `--concurrency` |
| Files → library via a session | [`migrate_session.py`](./migrate_session.py) | Parallel workers |
| Files → library server-side | [`migrate_library_serverside.py`](./migrate_library_serverside.py) | Versions + ACLs |
| SPMT-style session | [`migrate_spmt.py`](./migrate_spmt.py) | Register → task → start |
| Whole-site (same tenant) | [`migrate_site.py`](./migrate_site.py) | `migrate_all` → one job per list; `--preserve` for best-effort timestamps/authorship/ACLs; also copies web navigation, each web's title/description (`--no-site-settings`) and its site pages — modern canvases and classic wiki bodies (`--no-pages` / `--duplicate-pages`) — and reports publishing pages, wiki markup and web-part bindings as a handoff |
| Build a package offline | [`package_library.py`](./package_library.py) | Inspect the manifest, no tenant |
