"""
SharePoint site usage — storage and file counts per site.

The per-site usage report is the basis for SharePoint storage governance: which
sites consume the most, how many files they hold, and when they were last used.
The report can be large (one row per site), so by default only the largest sites
are listed; the totals always cover every site.

    python sharepoint_sites.py
    python sharepoint_sites.py --period D90 --limit 10
    python sharepoint_sites.py --include-deleted

Requires application permission ``Reports.Read.All`` (delegated works too).

https://learn.microsoft.com/en-us/graph/api/reportroot-getsharepointsiteusagedetail
"""

from __future__ import annotations

import argparse
import csv
import io

from office365.graph_client import GraphClient
from tests.settings import client_id, client_secret, tenant

GIB = 1024**3


def _rows(result) -> list[dict]:
    """Decode a report result into CSV rows (the CSV carries a UTF-8 BOM)."""
    value = result.value
    text = value.decode("utf-8-sig") if isinstance(value, bytes) else (value.content or b"").decode("utf-8-sig")
    return list(csv.DictReader(io.StringIO(text)))


def _storage(row: dict) -> float:
    try:
        return float(row.get("Storage Used (Byte)") or 0)
    except ValueError:
        return 0.0


def main() -> None:
    parser = argparse.ArgumentParser(description="SharePoint per-site storage")
    parser.add_argument("--period", default="D30", help="Aggregation period: D7/D30/D90/D180 (default: D30)")
    parser.add_argument("--limit", type=int, default=20, help="How many largest sites to list (default: 20)")
    parser.add_argument("--include-deleted", action="store_true", help="Also count deleted sites")
    args = parser.parse_args()

    client = GraphClient(tenant=tenant).with_client_secret(client_id, client_secret)
    rows = _rows(client.reports.get_sharepoint_site_usage_detail(args.period).execute_query())
    if not args.include_deleted:
        rows = [r for r in rows if (r.get("Is Deleted") or "").lower() != "true"]

    total = sum(_storage(r) for r in rows)
    print(f"SharePoint sites ({args.period}): {len(rows):,} site(s), {total / GIB:,.2f} GiB total\n")

    named = [r for r in rows if r.get("Site URL")]
    concealed = not named
    if concealed:
        named = rows
        print("(Site URLs are concealed — this tenant has report privacy enabled.)")

    def _label(row: dict) -> str:
        url = row.get("Site URL")
        if url:
            return url[:70]
        template = row.get("Root Web Template") or "site"
        deleted = " (deleted)" if (row.get("Is Deleted") or "").lower() == "true" else ""
        return f"{template}{deleted}  {row.get('Owner Display Name') or ''}"[:70]

    print(f"Largest {min(args.limit, len(named))} of {len(named):,} sites by storage:")
    for row in sorted(named, key=_storage, reverse=True)[: args.limit]:
        print(f"  {_storage(row) / GIB:8.2f} GiB  {int(row.get('File Count') or 0):>7,} files  {_label(row)}")


if __name__ == "__main__":
    main()
