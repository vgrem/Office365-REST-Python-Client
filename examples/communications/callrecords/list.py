"""
List Teams call records — the raw feed behind call-quality and telephony reports.

The feed is **application-only** (``CallRecords.Read.All``): there is no "my
calls" version, and it rejects ``$top``. Records are retained for 30 days, so
filter on ``startDateTime`` and bound the printed rows client-side.

https://learn.microsoft.com/en-us/graph/api/callrecords-callrecord-list
"""

import argparse
from datetime import datetime, timedelta, timezone

from office365.graph_client import GraphClient
from tests.settings import client_id, client_secret, tenant


def main():
    parser = argparse.ArgumentParser(description="List recent call records")
    parser.add_argument("--days", type=int, default=7, help="how far back to look (max 30)")
    parser.add_argument("--limit", type=int, default=20, help="how many rows to print")
    args = parser.parse_args()

    client = GraphClient(tenant=tenant).with_client_secret(client_id, client_secret)
    since = (datetime.now(timezone.utc) - timedelta(days=args.days)).strftime("%Y-%m-%dT%H:%M:%SZ")
    feed = client.communications.call_records.filter(f"startDateTime ge {since}")

    # ``$top`` is rejected by this feed (see CallRecordCollection.query_capabilities),
    # so the page is fetched and truncated here.
    records = list(feed.get().execute_query())[: args.limit]

    print(f"Call records since {since} ({len(records)}):\n")
    for record in records:
        start = record.start_date_time
        duration = (record.end_date_time - start).total_seconds() if record.end_date_time and start.year > 1 else None
        print(
            f"  {start:%Y-%m-%d %H:%M}  {record.type_.name:<22} "
            f"{f'{duration:.0f}s' if duration else '?':>7}  {len(record.participants)} participant(s)"
        )


if __name__ == "__main__":
    main()
