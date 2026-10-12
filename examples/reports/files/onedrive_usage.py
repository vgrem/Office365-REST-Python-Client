"""
OneDrive usage — file counts and storage.

Activity shows who is using OneDrive; *usage* shows what is stored there. Two
reports together:

* **file counts** — total files vs active files (saved, synced, modified or
  shared within the period);
* **storage** — bytes stored in OneDrive, per day.

    python onedrive_usage.py
    python onedrive_usage.py --period D90

Requires application permission ``Reports.Read.All`` (delegated works too).

https://learn.microsoft.com/en-us/graph/api/reportroot-getonedriveusagefilecounts
https://learn.microsoft.com/en-us/graph/api/reportroot-getonedriveusagestorage
"""

from __future__ import annotations

import argparse

from office365.graph_client import GraphClient
from tests.settings import client_id, client_secret, tenant

GIB = 1024**3


def main() -> None:
    parser = argparse.ArgumentParser(description="OneDrive file counts and storage")
    parser.add_argument("--period", default="D30", help="Aggregation period: D7/D30/D90/D180 (default: D30)")
    args = parser.parse_args()

    client = GraphClient(tenant=tenant).with_client_secret(client_id, client_secret)
    files = client.reports.get_onedrive_usage_file_counts(args.period).execute_query().csv_rows()
    storage = client.reports.get_onedrive_usage_storage(args.period).execute_query().csv_rows()

    storage = [r for r in storage if (r.get("Site Type") or "") == "OneDrive"] or storage

    if files:
        latest = max(files, key=lambda r: r.get("Report Date") or "")
        print(
            f"Files ({latest.get('Report Date')}): {int(latest.get('Total') or 0):,} total, "
            f"{int(latest.get('Active') or 0):,} active"
        )

    if storage:
        print(f"\nStorage over {len(storage)} day(s):")
        for row in sorted(storage, key=lambda r: r.get("Report Date") or "")[-7:]:
            gib = float(row.get("Storage Used (Byte)") or 0) / GIB
            print(f"  {(row.get('Report Date') or '?')[:10]}  {gib:6.2f} GiB")


if __name__ == "__main__":
    main()
