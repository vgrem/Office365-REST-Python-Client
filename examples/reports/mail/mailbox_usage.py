"""
Mailbox usage — storage, mailbox counts, and quota status.

Three Exchange Online reports that belong together when you plan storage or hunt
for mailboxes that are close to their quota:

* **storage** — bytes used by all mailboxes, per day;
* **mailbox counts** — total vs active mailboxes;
* **quota status** — how many mailboxes are under limit, warned, or blocked.

    python mailbox_usage.py
    python mailbox_usage.py --period D90

Requires application permission ``Reports.Read.All`` (delegated works too).

https://learn.microsoft.com/en-us/graph/api/reportroot-getmailboxusagestorage
https://learn.microsoft.com/en-us/graph/api/reportroot-getmailboxusagemailboxcounts
https://learn.microsoft.com/en-us/graph/api/reportroot-getmailboxusagequotastatusmailboxcounts
"""

from __future__ import annotations

import argparse

from office365.graph_client import GraphClient
from tests.settings import client_id, client_secret, tenant

GIB = 1024**3


def _latest(rows: list[dict]) -> dict:
    """The row for the most recent report date."""
    return max(rows, key=lambda r: r.get("Report Date") or "", default={})


def _gib(value) -> float:
    return float(value or 0) / GIB


def main() -> None:
    parser = argparse.ArgumentParser(description="Mailbox storage, counts, and quota status")
    parser.add_argument("--period", default="D30", help="Aggregation period: D7/D30/D90/D180 (default: D30)")
    args = parser.parse_args()

    client = GraphClient(tenant=tenant).with_client_secret(client_id, client_secret)
    storage = client.reports.get_mailbox_usage_storage(args.period).execute_query().csv_rows()
    counts = client.reports.get_mailbox_usage_mailbox_counts(args.period).execute_query().csv_rows()
    quota = client.reports.get_mailbox_usage_quota_status_mailbox_counts(args.period).execute_query().csv_rows()

    print(f"Mailbox storage ({args.period}) — {len(storage)} day(s)")
    if storage:
        storage = sorted(storage, key=lambda r: r.get("Report Date") or "")
        first, last = storage[0], storage[-1]
        delta = _gib(last.get("Storage Used (Byte)")) - _gib(first.get("Storage Used (Byte)"))
        print(f"  {(first.get('Report Date') or '?')[:10]}  {_gib(first.get('Storage Used (Byte)')):.2f} GiB")
        print(f"  {(last.get('Report Date') or '?')[:10]}  {_gib(last.get('Storage Used (Byte)')):.2f} GiB")
        print(f"  change: {delta:+.2f} GiB over the period")

    latest_counts = _latest(counts)
    if latest_counts:
        print(
            f"\nMailboxes — {latest_counts.get('Total') or 0} total, "
            f"{latest_counts.get('Active') or 0} active "
            f"({latest_counts.get('Report Date')})"
        )

    latest_quota = _latest(quota)
    if latest_quota:
        print(f"\nQuota status ({latest_quota.get('Report Date')}):")
        for label in ("Under Limit", "Warning Issued", "Send Prohibited", "Send/Receive Prohibited", "Indeterminate"):
            value = latest_quota.get(label)
            if value not in (None, ""):
                print(f"  {label:26s} {value}")


if __name__ == "__main__":
    main()
