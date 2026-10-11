"""
Copy events between calendars — for migration, backup, or reorganization.

Selects events from the signed-in user's default calendar and recreates them in
a target calendar (default: the same calendar, so nothing is lost). Useful when
moving events between personal and shared calendars, or during offboarding.

Requires delegated permission ``Calendars.ReadWrite``.

https://learn.microsoft.com/en-us/graph/api/user-post-events
"""

from __future__ import annotations

import argparse
from datetime import datetime, timedelta, timezone

from office365.graph_client import GraphClient
from tests.settings import client_id, password, tenant, username


def main() -> None:
    parser = argparse.ArgumentParser(description="Copy recent events to another calendar")
    parser.add_argument("--days", type=int, default=30, help="copy events from the last N days (default: 30)")
    parser.add_argument("--calendar-id", help="target calendar id (default: the signed-in user's calendar)")
    parser.add_argument("--apply", action="store_true", help="actually create the copies")
    args = parser.parse_args()

    client = GraphClient(tenant=tenant).with_username_and_password(client_id, username, password)

    end = datetime.now(timezone.utc)
    start = end - timedelta(days=args.days)
    start_literal = start.strftime("%Y-%m-%dT%H:%M:%SZ")
    end_literal = end.strftime("%Y-%m-%dT%H:%M:%SZ")
    events = (
        client.me.calendar.events.filter(f"start/dateTime ge '{start_literal}' and end/dateTime le '{end_literal}'")
        .get()
        .execute_query()
    )
    print(f"Found {len(events)} event(s) in the last {args.days} days")

    if not args.apply:
        for event in list(events)[:5]:
            print(f"  would copy: {event.subject}")
        print("Dry run — re-run with --apply to copy.")
        return

    target = client.me.calendars[args.calendar_id] if args.calendar_id else client.me.calendar
    for event in events:
        target.events.add(
            subject=event.subject, body=event.body_preview or "", start=event.start, end=event.end
        ).execute_query()
        print(f"  Copied: {event.subject}")
    print(f"\nCopied {len(events)} event(s)")


if __name__ == "__main__":
    main()
