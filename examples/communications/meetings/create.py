"""
Create a Teams online meeting and print its join URL.

The meeting is standalone: nothing is added to anyone's calendar. To put it
there, send the join URL as an event body (see the `online_meeting.py` example
under `examples/outlook/events/`).

Requires the delegated permission ``OnlineMeetings.ReadWrite``.

https://learn.microsoft.com/en-us/graph/api/application-post-onlinemeetings
"""

import argparse
from datetime import datetime, timedelta, timezone

from office365.graph_client import GraphClient
from tests.settings import client_id, password, tenant, username

LOBBY_SCOPES = [
    "organizer",
    "organization",
    "organizationAndFederated",
    "organizationExcludingGuests",
    "invited",
    "everyone",
]


def main():
    parser = argparse.ArgumentParser(description="Create an online meeting")
    parser.add_argument("--subject", default="Project sync", help="meeting subject")
    parser.add_argument("--minutes", type=int, default=60, help="duration in minutes")
    parser.add_argument(
        "--lobby",
        default="organization",
        choices=LOBBY_SCOPES,
        help="who may bypass the lobby",
    )
    args = parser.parse_args()

    client = GraphClient(tenant=tenant).with_username_and_password(client_id, username, password)
    start = datetime.now(timezone.utc) + timedelta(hours=1)

    meeting = client.me.online_meetings.create(
        subject=args.subject,
        start_datetime=start,
        end_datetime=start + timedelta(minutes=args.minutes),
        lobbyBypassSettings={"isDialInBypassEnabled": True, "scope": args.lobby},
    ).execute_query()

    print(f"Created '{meeting.subject}'")
    print(f"  id       : {meeting.id}")
    print(f"  join URL : {meeting.join_web_url}")
    print(f"  starts   : {meeting.start_date_time}")


if __name__ == "__main__":
    main()
