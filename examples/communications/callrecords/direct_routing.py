"""
The Direct Routing call log — the PSTN side of Teams telephony.

``getDirectRoutingCalls`` returns a **flat log**, not entities: the rows are
``DirectRoutingLogRow`` values wrapped in a ``ClientResult``, so read
``.value`` before iterating. Use it to trace calls that left the tenant through
your SBC: which number dialed which, and the final SIP response.

Requires the application permission ``CallRecords.Read.All``.

https://learn.microsoft.com/en-us/graph/api/callrecords-callrecord-getdirectroutingcalls
"""

import argparse
from datetime import datetime, timedelta, timezone

from office365.graph_client import GraphClient
from tests.settings import client_id, client_secret, tenant


def main():
    parser = argparse.ArgumentParser(description="Show the Direct Routing call log")
    parser.add_argument("--days", type=int, default=7, help="how far back to look")
    parser.add_argument("--limit", type=int, default=20, help="how many rows to print")
    args = parser.parse_args()

    client = GraphClient(tenant=tenant).with_client_secret(client_id, client_secret)
    to_datetime = datetime.now(timezone.utc)

    rows = (
        client.communications.call_records.get_direct_routing_calls(
            from_datetime=to_datetime - timedelta(days=args.days),
            to_datetime=to_datetime,
        )
        .execute_query()
        .value
    )

    print(f"{len(rows)} Direct Routing call(s) in the last {args.days} day(s)\n")
    for row in rows[: args.limit]:
        outcome = row.finalSipCodePhrase or ("answered" if row.successfulCall else "failed")
        print(f"  {row.startDateTime}  {row.callerNumber} -> {row.calleeNumber}  {row.callType}  {outcome}")


if __name__ == "__main__":
    main()
