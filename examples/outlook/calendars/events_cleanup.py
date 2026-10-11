"""
Clean up old calendar events — dry-run, then delete.

Finds events that ended more than N days ago and, with ``--apply``, deletes them.
Dry-run by default, so it is safe to try. Useful for mailbox maintenance.

Requires delegated permission ``Calendars.ReadWrite``.

https://learn.microsoft.com/en-us/graph/api/event-delete
"""

from __future__ import annotations

import argparse
from datetime import datetime, timedelta, timezone

from office365.graph_client import GraphClient
from tests.settings import client_id, password, tenant, username

PREVIEW_LIMIT = 5


def main() -> None:
    parser = argparse.ArgumentParser(description="Delete calendar events older than N days (dry-run unless --apply)")
    parser.add_argument("--days", type=int, default=365, help="age threshold in days (default: 365)")
    parser.add_argument("--apply", action="store_true", help="actually delete the events")
    args = parser.parse_args()

    client = GraphClient(tenant=tenant).with_username_and_password(client_id, username, password)

    cutoff = datetime.now(timezone.utc) - timedelta(days=args.days)
    cutoff_literal = cutoff.strftime("%Y-%m-%dT%H:%M:%SZ")
    events = client.me.calendar.events.filter(f"end/dateTime lt '{cutoff_literal}'").get().execute_query()
    print(f"Found {len(events)} event(s) older than {args.days} days")

    if not args.apply:
        for event in list(events)[:PREVIEW_LIMIT]:
            print(f"  {event.subject}  ({event.start} — {event.end})")
        if len(events) > PREVIEW_LIMIT:
            print(f"  ... and {len(events) - PREVIEW_LIMIT} more")
        print("Dry run — re-run with --apply to delete.")
        return

    for event in events:
        event.delete_object().execute_query()
    print(f"Deleted {len(events)} event(s)")


if __name__ == "__main__":
    main()
