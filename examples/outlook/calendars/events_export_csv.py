"""
Export calendar events to CSV — subject, organizer, attendees, time, recurrence.

Useful for auditing, reporting, or migrating calendar data. Reads the signed-in
user's calendar, so it needs **delegated** auth (``/me`` is invalid for app-only).

Requires delegated permission ``Calendars.Read``.

https://learn.microsoft.com/en-us/graph/api/user-list-events
"""

from __future__ import annotations

import argparse
import csv
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path

from office365.graph_client import GraphClient
from tests.settings import client_id, password, tenant, username


def main() -> None:
    parser = argparse.ArgumentParser(description="Export calendar events to CSV")
    parser.add_argument("--days", type=int, default=90, help="look back this many days (default: 90)")
    parser.add_argument(
        "--output", default=str(Path(tempfile.gettempdir()) / "calendar_export.csv"), help="CSV output path"
    )
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

    with open(args.output, "w", newline="", encoding="utf-8") as stream:
        writer = csv.writer(stream)
        writer.writerow(["subject", "organizer", "start", "end", "attendees", "recurrence"])
        for event in events:
            attendees = "; ".join(a.emailAddress.address or "" for a in (event.attendees or []))
            writer.writerow(
                [
                    event.subject or "",
                    event.organizer.emailAddress.address if event.organizer else "",
                    event.start,
                    event.end,
                    attendees,
                    event.recurrence.pattern.type if event.recurrence and event.recurrence.pattern else "",
                ]
            )

    print(f"Exported {len(events)} event(s) to {args.output}")


if __name__ == "__main__":
    main()
