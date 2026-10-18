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
| Whole-site (same tenant) | [`migrate_site.py`](./migrate_site.py) | `migrate_all` → one job per list; `--preserve` for best-effort timestamps/authorship/ACLs (web groups, web role assignments **and** each list's own ACLs, replayed after the content); also copies web navigation, each web's title/description (`--no-site-settings`) and its site pages — modern canvases and classic wiki bodies (`--no-pages` / `--duplicate-pages`) — and reports publishing pages, wiki markup and web-part bindings as a handoff |
| Build a package offline | [`package_library.py`](./package_library.py) | Inspect the manifest, no tenant |

## Tuning a run

`migrate_site.py` reports the rate each list achieved, so a tuning change is judged
on a number rather than a feeling:

```bash
python migrate_site.py --source-site https://contoso.sharepoint.com/sites/a \
  --target-site https://contoso.sharepoint.com/sites/b \
  --lists-in-flight 4 --concurrency 4 --batch-size 50 --pace 0.25 --stats 30 --apply
```

| Flag | What it changes |
|------|-----------------|
| `--lists-in-flight N` | lists migrated at the same time — the site-level knob: a site of many small lists is waiting on per-list round trips, so overlapping lists (not more workers per list) is what shortens the run |
| `--concurrency N` | parallel workers per list — most help on many small files, none on a few large ones (the upload session is already the bottleneck) |
| `--batch-size N` | items per `$batch` and how often progress/checkpoints flush |
| `--pace SECONDS` | a fleet-wide floor between requests (`RateLimiter`), the proactive answer to a tenant that throttles |
| `--stats N` | heartbeat per active list instead of silence between `Migrating…` and the summary |

`--lists-in-flight` is usually the bigger of the two parallelism knobs, and the
cheapest to justify: each list keeps its own manifest and checkpoint, every worker
runs on a context clone that shares the login and the connection pool, and
`--pace` still bounds the whole run because the limiter is shared. The pilot shape —
24 lists, 6 site pages, a fresh target — is exactly the case it fixes.

Every run also prints how much the service pushed back: `throttling: none (171
request(s))` or `throttling: throttled 3/171 response(s) (429: 2, 503: 1), 42s of
Retry-After`. Raise `--concurrency`, and if throttling rises with the rate, the
new number is the tenant's ceiling rather than the copy's speed — back off with
`--pace` instead. `--log-json` carries the same counters as `throttled` events and
in `run.completed`, so the curve can be charted from a collector.

See [Throttling as a measured number](https://github.com/vgrem/office365-rest-python-client/blob/main/docs/migration.md#throttling-as-a-measured-number).
