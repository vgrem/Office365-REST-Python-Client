"""
Copilot usage from the Microsoft 365 apps usage report.

When Copilot is licensed, ``getM365AppUserCounts`` gains a ``Copilot`` column
next to Outlook, Word, Excel and so on. This script isolates that column and
prints Copilot active users per day, plus the peak.

Tenants without Copilot licenses have no such column; the script says so and
exits cleanly.

    python usage_report.py
    python usage_report.py --period D30

Requires application permission ``Reports.Read.All`` (delegated works too).

https://learn.microsoft.com/en-us/graph/api/reportroot-getm365appusercounts
"""

from __future__ import annotations

import argparse
import csv
import io

from office365.graph_client import GraphClient
from tests.settings import client_id, client_secret, tenant


def _rows(result) -> list[dict]:
    """Decode a report result into CSV rows (the CSV carries a UTF-8 BOM)."""
    value = result.value
    text = value.decode("utf-8-sig") if isinstance(value, bytes) else (value.content or b"").decode("utf-8-sig")
    return list(csv.DictReader(io.StringIO(text)))


def _int(value) -> int:
    try:
        return int(value or 0)
    except ValueError:
        return 0


def main() -> None:
    parser = argparse.ArgumentParser(description="Copilot usage from the M365 apps report")
    parser.add_argument("--period", default="D30", help="Aggregation period: D7/D30/D90/D180 (default: D30)")
    args = parser.parse_args()

    client = GraphClient(tenant=tenant).with_client_secret(client_id, client_secret)
    rows = _rows(client.reports.get_m365_app_user_counts(args.period).execute_query())

    copilot_columns = [c for c in (rows[0] if rows else {}) if "copilot" in c.lower()]
    if not copilot_columns:
        print(f"No Copilot column in the M365 apps report for {args.period}.")
        print("The tenant has no Copilot licenses assigned, so the report has nothing to show.")
        return

    column = copilot_columns[0]
    print(f"Copilot active users ({args.period}), column '{column}':\n")
    peak = 0
    for row in sorted(rows, key=lambda r: r.get("Report Date") or ""):
        value = _int(row.get(column))
        peak = max(peak, value)
        print(f"  {(row.get('Report Date') or '?')[:10]}  {value:>6,}")

    print(f"\nPeak: {peak:,} active Copilot user(s)")


if __name__ == "__main__":
    main()
