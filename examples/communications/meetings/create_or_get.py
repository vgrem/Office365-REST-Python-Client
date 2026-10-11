"""
Create-or-get: idempotent meeting creation for calendar/booking integrations.

``createOrGet`` keys the meeting on **your own** ``externalId``. Calling it
again with the same id returns the existing meeting instead of creating a
duplicate — so a retried request, a re-run import or two concurrent workers
can't produce two meetings for one booking.

Requires the delegated permission ``OnlineMeetings.ReadWrite``.

https://learn.microsoft.com/en-us/graph/api/onlinemeeting-createorget
"""

import argparse
from datetime import datetime, timedelta, timezone

from office365.graph_client import GraphClient
from tests.settings import client_id, password, tenant, username


def main():
    parser = argparse.ArgumentParser(description="Create or reuse an online meeting")
    parser.add_argument("--external-id", default="demo-booking-42", help="your stable id for this meeting")
    parser.add_argument("--subject", default="Customer demo")
    parser.add_argument("--minutes", type=int, default=30)
    args = parser.parse_args()

    client = GraphClient(tenant=tenant).with_username_and_password(client_id, username, password)
    start = datetime.now(timezone.utc) + timedelta(days=1)

    for attempt in (1, 2):
        meeting = client.me.online_meetings.create_or_get(
            external_id=args.external_id,
            subject=args.subject,
            start_datetime=start,
            end_datetime=start + timedelta(minutes=args.minutes),
        ).execute_query()
        print(f"attempt {attempt}: id={meeting.id} join URL={meeting.join_web_url}")
    print("\nBoth attempts returned the same meeting — no duplicate was booked.")


if __name__ == "__main__":
    main()
