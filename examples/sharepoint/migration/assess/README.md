# Step 2 — Scan and assess

Pre-migration readiness review. Part of [Migration](../README.md).

| What | File | Notes |
|------|------|-------|
| Assess a site | [`assess_site.py`](./assess_site.py) | Site + subsites, blockers/warnings |
| Bulk assess | [`assess_bulk.py`](./assess_bulk.py) | Tenant-wide readiness |
| Capture list structure | [`capture_structure.py`](./capture_structure.py) | Columns/content types/views to JSON (read-only) |
| Large Sites scan report | [`reports/large_sites.py`](./reports/large_sites.py) | SMAT-style `LargeSites-detail` |

See [reports/](./reports/README.md) for the generated SMAT scan reports.
