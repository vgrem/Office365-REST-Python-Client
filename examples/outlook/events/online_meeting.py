"""
Create an event as a Microsoft Teams online meeting.

Set ``onlineMeetingProvider`` (and ``isOnlineMeeting``) when creating an event and
Graph — via Teams — generates a join link, instead of you pasting a meeting URL
into the body. The link is read back from ``event.online_meeting.join_url``.

Requires delegated permission ``Calendars.ReadWrite``.

https://learn.microsoft.com/en-us/graph/api/resources/event
https://learn.microsoft.com/en-us/graph/api/resources/onlinemeetinginfo
"""

from __future__ import annotations

import argparse
from datetime import datetime, timedelta, timezone

from office365.graph_client import GraphClient
from tests.settings import client_id, password, tenant, username


def main() -> None:
    parser = argparse.ArgumentParser(description="Create a Teams online meeting")
    parser.add_argument("--keep", action="store_true", help="keep the created event")
    args = parser.parse_args()

    client = GraphClient(tenant=tenant).with_username_and_password(client_id, username, password)

    start = datetime.now(timezone.utc) + timedelta(days=1)
    event = client.me.calendar.events.add(
        subject="Online sync",
        body="Join with the link below.",
        start=start,
        end=start + timedelta(minutes=30),
        isOnlineMeeting=True,
        onlineMeetingProvider="teamsForBusiness",
    ).execute_query()

    print(f"Event: {event.subject}")
    print(f"  online meeting: {event.is_online_meeting}  provider={event.online_meeting_provider}")
    join_url = event.online_meeting.join_url if event.online_meeting else None
    print(f"  join URL: {join_url or '(none)'}")

    if not args.keep:
        event.delete_object().execute_query()
        print("Deleted.")


if __name__ == "__main__":
    main()
