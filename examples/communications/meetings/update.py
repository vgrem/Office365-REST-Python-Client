"""
Change a meeting's conference options after it was created.

``allowMeetingChat``, ``allowTranscription``, ``lobbyBypassSettings`` and
friends are **read-only in this client** — there is no Python setter — so they
are written with ``set_property`` and PATCHed. ``update()`` sends only the
properties you touched.

Two quirks worth knowing:

* ``lobbyBypassSettings`` is normalized to ``unknownFutureValue`` when it is
  sent half-empty (always include ``isDialInBypassEnabled``) or batched with
  other properties — set it on creation instead, see ``create.py``.
* an empty string is not "unset": ``None`` removes a property from the payload.

Requires the delegated permission ``OnlineMeetings.ReadWrite``.

https://learn.microsoft.com/en-us/graph/api/onlinemeeting-update
"""

import argparse
from datetime import datetime, timedelta, timezone

from office365.graph_client import GraphClient
from tests.settings import client_id, password, tenant, username


def main():
    parser = argparse.ArgumentParser(description="Update meeting options")
    parser.add_argument("--chat", default="disabled", choices=["enabled", "disabled"])
    parser.add_argument("--transcription", default="enabled", choices=["enabled", "disabled"])
    args = parser.parse_args()

    client = GraphClient(tenant=tenant).with_username_and_password(client_id, username, password)
    start = datetime.now(timezone.utc) + timedelta(hours=3)

    meeting = client.me.online_meetings.create(
        subject="Update demo",
        start_datetime=start,
        end_datetime=start + timedelta(minutes=30),
    ).execute_query()

    meeting.set_property("allowMeetingChat", args.chat)
    meeting.set_property("allowTranscription", args.transcription == "enabled")
    meeting.update().execute_query()
    print(f"PATCHed meeting {meeting.id}")

    refreshed = client.me.online_meetings[meeting.id].get().execute_query()
    print(f"  allowMeetingChat     : {refreshed.allow_meeting_chat}")
    print(f"  allowTranscription   : {refreshed.allow_transcription}")

    refreshed.delete_object().execute_query()
    print("Cleaned up.")


if __name__ == "__main__":
    main()
