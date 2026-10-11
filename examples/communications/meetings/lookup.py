"""
Find an online meeting — by its id, or by the join URL from the invite.

There is no "list all my online meetings": ``/me/onlineMeetings`` without a
filter returns *InvalidArgument*, and the only supported filter is
``JoinWebUrl``. In practice you either keep the meeting id returned by
``create``, or you pull the join URL out of the calendar invite and resolve it
back here.

Requires the delegated permission ``OnlineMeetings.Read`` (plus ``ReadWrite`` to
create the throwaway meeting this demo uses).
"""

import argparse
from datetime import datetime, timedelta, timezone

from office365.graph_client import GraphClient
from tests.settings import client_id, password, tenant, username


def main():
    parser = argparse.ArgumentParser(description="Look up an online meeting")
    parser.add_argument("--meeting-id", help="object id, e.g. from create.py")
    parser.add_argument("--join-url", help="joinWebUrl, e.g. from a calendar invite")
    args = parser.parse_args()

    client = GraphClient(tenant=tenant).with_username_and_password(client_id, username, password)

    temporary = None
    if not args.meeting_id and not args.join_url:
        start = datetime.now(timezone.utc) + timedelta(hours=2)
        temporary = client.me.online_meetings.create(
            subject="Lookup demo",
            start_datetime=start,
            end_datetime=start + timedelta(minutes=30),
        ).execute_query()
        args.meeting_id, args.join_url = temporary.id, temporary.join_web_url
        print(f"No id given — created a throwaway meeting {args.meeting_id}\n")

    by_id = client.me.online_meetings[args.meeting_id].get().execute_query()
    print(f"by id       : {by_id.subject!r} (starts {by_id.start_date_time})")

    found = client.me.online_meetings.filter(f"JoinWebUrl eq '{args.join_url}'").get().execute_query()
    print(f"by join URL : {len(found)} match(es) -> {found[0].subject!r}" if found else "by join URL : no match")

    if temporary is not None:
        client.me.online_meetings[args.meeting_id].delete_object().execute_query()
        print("\nThrowaway meeting deleted.")


if __name__ == "__main__":
    main()
