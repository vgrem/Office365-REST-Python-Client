"""
Recordings, transcripts and attendance reports — the meeting artifacts.

These live under a meeting (``/onlineMeetings/{id}/recordings`` …) and each one
has its own permission, which is often *not* granted: this demo reports what the
tenant allows instead of failing. Attendance reports additionally need
``OnlineMeetingArtifact.Read.All`` and are only ready after the meeting ends.

Requires the delegated permission ``OnlineMeetings.Read`` — and, per artifact,
``OnlineMeetingRecording.Read.All`` / ``OnlineMeetingTranscript.Read.All`` /
``OnlineMeetingArtifact.Read.All``.
"""

import argparse
from datetime import datetime, timedelta, timezone

from office365.graph_client import GraphClient
from office365.runtime.client_request_exception import ClientRequestException
from tests.settings import client_id, password, tenant, username

ARTIFACTS = [
    ("recordings", "recordings", "OnlineMeetingRecording.Read.All"),
    ("transcripts", "transcripts", "OnlineMeetingTranscript.Read.All"),
    ("attendance reports", "attendance_reports", "OnlineMeetingArtifact.Read.All"),
]


def main():
    parser = argparse.ArgumentParser(description="List a meeting's artifacts")
    parser.add_argument("--meeting-id", help="an ended meeting; defaults to a fresh throwaway one")
    args = parser.parse_args()

    client = GraphClient(tenant=tenant).with_username_and_password(client_id, username, password)

    meeting_id = args.meeting_id
    if meeting_id is None:
        start = datetime.now(timezone.utc) + timedelta(hours=1)
        meeting = client.me.online_meetings.create(
            subject="Artifacts demo",
            start_datetime=start,
            end_datetime=start + timedelta(minutes=30),
        ).execute_query()
        meeting_id = meeting.id
        print(f"No --meeting-id given — using throwaway meeting {meeting_id}\n")

    target = client.me.online_meetings[meeting_id]
    for label, navigation, permission in ARTIFACTS:
        collection = getattr(target, navigation)
        try:
            items = collection.get().execute_query()
            print(f"{label:<18}: {len(items)} item(s)")
            for item in items:
                print(f"    {item.id}  {getattr(item, 'created_date_time', '')}")
        except ClientRequestException as e:
            print(f"{label:<18}: unavailable ({e.code}) — grant {permission}, and attend the meeting first")


if __name__ == "__main__":
    main()
