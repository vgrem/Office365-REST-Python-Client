"""
Email activity — sends, receives, and reads per day.

The Exchange Online activity report is the pulse of mail usage: how many
messages were sent, received and read each day over the reporting period. Use it
to spot usage trends and to justify (or reclaim) mail licensing.

    python activity.py
    python activity.py --period D90

Requires application permission ``Reports.Read.All`` (delegated works too).

https://learn.microsoft.com/en-us/graph/api/reportroot-getemailactivitycounts
"""

from __future__ import annotations

import argparse
import csv
import io

from office365.graph_client import GraphClient
from tests.settings import client_id, client_secret, tenant


def _rows(result) -> list[dict]:
    """Decode a report result into CSV rows.

    Graph returns the CSV with a UTF-8 BOM on the first header, so decode with
    ``utf-8-sig`` to keep ``\"Report Date\"`` (and friends) addressable.
    """
    value = result.value
    text = value.decode("utf-8-sig") if isinstance(value, bytes) else (value.content or b"").decode("utf-8-sig")
    return list(csv.DictReader(io.StringIO(text)))


def main() -> None:
    parser = argparse.ArgumentParser(description="Email activity (send / receive / read)")
    parser.add_argument("--period", default="D30", help="Aggregation period: D7/D30/D90/D180 (default: D30)")
    args = parser.parse_args()

    client = GraphClient(tenant=tenant).with_client_secret(client_id, client_secret)
    rows = _rows(client.reports.get_email_activity_counts(args.period).execute_query())

    print(f"Email activity ({args.period}) — {len(rows)} day(s)\n")
    print(f"{'Date':12s}  {'Sent':>8s}  {'Received':>9s}  {'Read':>8s}")
    totals = {"Send": 0, "Receive": 0, "Read": 0}
    for row in sorted(rows, key=lambda r: r.get("Report Date") or ""):
        for key in totals:
            totals[key] += int(row.get(key) or 0)
        print(
            f"{(row.get('Report Date') or '?')[:10]:12s}"
            f"  {int(row.get('Send') or 0):>8,}"
            f"  {int(row.get('Receive') or 0):>9,}"
            f"  {int(row.get('Read') or 0):>8,}"
        )

    print(f"\nTotals: {totals['Send']:,} sent, {totals['Receive']:,} received, {totals['Read']:,} read")


if __name__ == "__main__":
    main()
