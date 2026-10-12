"""
Microsoft 365 apps usage — active users per app.

The M365 apps report is one column per application (Outlook, Word, Excel,
PowerPoint, OneNote, Teams, and Copilot when licensed) with the number of active
users each day. It shows which apps people actually use — useful input for
licensing and adoption campaigns.

    python m365_apps.py
    python m365_apps.py --period D90

Requires application permission ``Reports.Read.All`` (delegated works too).

https://learn.microsoft.com/en-us/graph/api/reportroot-getm365appusercounts
"""

from __future__ import annotations

import argparse

from office365.graph_client import GraphClient
from tests.settings import client_id, client_secret, tenant

_META = {"Report Refresh Date", "Report Period", "Report Date"}


def _int(value) -> int:
    try:
        return int(value or 0)
    except ValueError:
        return 0


def main() -> None:
    parser = argparse.ArgumentParser(description="Active users per Microsoft 365 app")
    parser.add_argument("--period", default="D30", help="Aggregation period: D7/D30/D90/D180 (default: D30)")
    args = parser.parse_args()

    client = GraphClient(tenant=tenant).with_client_secret(client_id, client_secret)
    rows = client.reports.get_m365_app_user_counts(args.period).execute_query().csv_rows()

    if not rows:
        print(f"No M365 app data for {args.period}")
        return

    apps = [column for column in rows[0] if column not in _META]
    latest = max(rows, key=lambda r: r.get("Report Date") or "")
    print(f"Active users per app ({args.period}), latest day {latest.get('Report Date')}:\n")
    for app in sorted(apps, key=lambda a: -_int(latest.get(a))):
        peak = max((_int(r.get(app)) for r in rows), default=0)
        print(f"  {app:12s}  {_int(latest.get(app)):>5,}   (peak {peak:,})")


if __name__ == "__main__":
    main()
