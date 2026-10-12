"""
OneDrive activity — active users by activity type.

The OneDrive activity report counts the unique licensed users who viewed or
edited, synced, or shared files each day. It answers "is anyone actually using
OneDrive?" and separates internal from external sharing.

    python onedrive_activity.py
    python onedrive_activity.py --period D90

Requires application permission ``Reports.Read.All`` (delegated works too).

https://learn.microsoft.com/en-us/graph/api/reportroot-getonedriveactivityusercounts
"""

from __future__ import annotations

import argparse

from office365.graph_client import GraphClient
from tests.settings import client_id, client_secret, tenant

ACTIVITIES = ("Viewed Or Edited", "Synced", "Shared Internally", "Shared Externally")


def main() -> None:
    parser = argparse.ArgumentParser(description="OneDrive active users by activity type")
    parser.add_argument("--period", default="D30", help="Aggregation period: D7/D30/D90/D180 (default: D30)")
    args = parser.parse_args()

    client = GraphClient(tenant=tenant).with_client_secret(client_id, client_secret)
    rows = client.reports.get_onedrive_activity_user_counts(args.period).execute_query().csv_rows()

    print(f"OneDrive activity ({args.period}) — {len(rows)} day(s)\n")
    header = "  ".join(f"{name:>17s}" for name in ACTIVITIES)
    print(f"{'Date':12s}  {header}")
    totals = dict.fromkeys(ACTIVITIES, 0)
    for row in sorted(rows, key=lambda r: r.get("Report Date") or ""):
        cells = []
        for name in ACTIVITIES:
            value = int(row.get(name) or 0)
            totals[name] += value
            cells.append(f"{value:>17,}")
        print(f"{(row.get('Report Date') or '?')[:10]:12s}  " + "  ".join(cells))

    print("\nPeak / total active users (per activity):")
    for name in ACTIVITIES:
        peak = max((int(r.get(name) or 0) for r in rows), default=0)
        print(f"  {name:20s} peak {peak:>5,}   sum {totals[name]:>7,}")


if __name__ == "__main__":
    main()
