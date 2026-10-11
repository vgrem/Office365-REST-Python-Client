"""
Delete an online meeting, and confirm that it is really gone.

Deleting kills the join link; recordings and transcripts that belong to the
meeting are removed with it, so use this to clean up demo or abandoned
meetings. By default the script creates a throwaway meeting and deletes that,
which keeps it safe to re-run.

Requires the delegated permission ``OnlineMeetings.ReadWrite``.

https://learn.microsoft.com/en-us/graph/api/onlinemeeting-delete
"""

import argparse
from datetime import datetime, timedelta, timezone

from office365.graph_client import GraphClient
from office365.runtime.client_request_exception import ClientRequestException
from tests.settings import client_id, password, tenant, username


def main():
    parser = argparse.ArgumentParser(description="Delete an online meeting")
    parser.add_argument("--meeting-id", help="delete this meeting instead of a throwaway one")
    args = parser.parse_args()

    client = GraphClient(tenant=tenant).with_username_and_password(client_id, username, password)

    meeting_id = args.meeting_id
    if meeting_id is None:
        start = datetime.now(timezone.utc) + timedelta(hours=4)
        meeting = client.me.online_meetings.create(
            subject="Delete demo",
            start_datetime=start,
            end_datetime=start + timedelta(minutes=30),
        ).execute_query()
        meeting_id = meeting.id
        print(f"Created throwaway meeting {meeting_id}")

    client.me.online_meetings[meeting_id].delete_object().execute_query()
    print(f"DELETE /me/onlineMeetings/{meeting_id} -> 204")

    try:
        client.me.online_meetings[meeting_id].get().execute_query()
        print("...but the meeting is still there?!")
    except ClientRequestException as e:
        print(f"Re-reading it now returns {e.code} — confirmed gone.")


if __name__ == "__main__":
    main()
