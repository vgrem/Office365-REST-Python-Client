# Recipes

Cross-domain, end-to-end workflows that combine several SharePoint areas in one
runnable script. Run [getting-started](../getting-started/) once to create the
certificate and site access, then pick a recipe below.

The single-domain building blocks live in the [domain folders](../README.md);
these recipes show how they fit together for a realistic task.

---

## Prerequisites

| Requirement | Description |
|---|---|
| **Certificate auth** | Run [getting-started](../getting-started/) once. The recipes read `cert_path`, `cert_thumbprint`, `client_id`, `site_url`, `tenant` from `.env`. |
| **Site access** | `Sites.Selected` + a per-site grant (see getting-started), or `Sites.FullControl.All` for tenant-wide work. |
| **Write access** | Provisioning and upload recipes need read/write; the access recipe needs `Sites.FullControl.All` on the **calling** app. |

---

## The recipes

| Recipe | Combines | What it does |
|---|---|---|
| [`provision_project_workspace.py`](provision_project_workspace.py) | sites, lists, fields, views, list items | Idempotently creates a document library with typed columns, a task list with a view, and starter rows. |
| [`upload_folder_with_metadata.py`](upload_folder_with_metadata.py) | folders, files, fields, list items | Mirrors a local folder into a library, chunk-uploading large files and stamping metadata; skips unchanged files. |
| [`grant_app_site_access.py`](grant_app_site_access.py) | permissions, tenant, Entra apps | Bulk grants or revokes an app's `Sites.Selected` access across several sites via `Site.grant_app_access` / `revoke_app_access`. |
| [`search_content_inventory.py`](search_content_inventory.py) | search, files, tenant | Pages a search query into a CSV inventory, grouped by site and type, with a stale-document count. |

---

## Running a recipe

```bash
python provision_project_workspace.py
python upload_folder_with_metadata.py --source ./reports --library "Project Files"
python grant_app_site_access.py --app-id <client-id> --sites-file sites.txt
python search_content_inventory.py --output inventory.csv --stale-days 180
```

Every recipe supports `--help`; the ones that change content support `--dry-run`.

## Related

- [Getting started](../getting-started/) — one-time certificate and site access.
- [Domain folders](../README.md) — the full catalog, by area.
- [Async examples](../../patterns/async/) — awaitable twins for keeping an event loop free.
