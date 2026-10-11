"""
Set your own presence ("preferred presence") and status message.

A preferred presence overrides whatever Teams computes from your activity
until the expiration elapses (5–240 minutes) or you clear it. It only takes
effect while at least one presence session exists — that is, while Teams is
signed in.

Requires the delegated permission ``Presence.ReadWrite``.

https://learn.microsoft.com/en-us/graph/api/presence-setuserpreferredpresence
https://learn.microsoft.com/en-us/graph/api/presence-setstatusmessage
"""

import argparse
from datetime import datetime, timedelta, timezone

from office365.graph_client import GraphClient
from tests.settings import client_id, password, tenant, username


def main():
    parser = argparse.ArgumentParser(description="Set your preferred presence")
    parser.add_argument(
        "--availability",
        default="DoNotDisturb",
        help="Available, Busy, DoNotDisturb, Away, BeRightBack, Offline",
    )
    parser.add_argument("--activity", default="DoNotDisturb", help="activity that refines the availability")
    parser.add_argument("--minutes", type=int, default=120, help="how long the status lasts (5-240)")
    parser.add_argument("--message", default="In a meeting — will respond later", help="status message ('' to skip)")
    args = parser.parse_args()

    client = GraphClient(tenant=tenant).with_username_and_password(client_id, username, password)
    presence = client.me.presence

    presence.set_user_preferred_presence(
        availability=args.availability,
        activity=args.activity,
        expiration_duration=f"PT{args.minutes}M",
    ).execute_query()
    print(f"Presence set to {args.availability}/{args.activity} for {args.minutes} minute(s)")

    if args.message:
        presence.set_status_message(
            message=args.message,
            expiry=datetime.now(timezone.utc) + timedelta(minutes=args.minutes),
        ).execute_query()
        print(f"Status message set to {args.message!r}")


if __name__ == "__main__":
    main()
