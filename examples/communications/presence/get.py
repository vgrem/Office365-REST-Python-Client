"""
Read presence — your own, or (with a wider scope) another user's.

Requires the delegated permission ``Presence.Read`` for your own presence, or
``Presence.Read.All`` to read anyone else's.

https://learn.microsoft.com/en-us/graph/api/presence-get
"""

import argparse

from office365.communications.presences.presence import Presence
from office365.graph_client import GraphClient
from tests.settings import client_id, password, tenant, username


def describe(label: str, presence: Presence) -> None:
    print(f"{label}")
    print(f"  availability : {presence.availability}")
    print(f"  activity     : {presence.activity}")
    status = presence.status_message
    if status is not None and status.message is not None and status.message.content:
        print(f"  message      : {status.message.content}")
    if presence.work_location is not None:
        print(f"  work location: {presence.work_location.work_location_type}")


def main():
    parser = argparse.ArgumentParser(description="Read a user's presence")
    parser.add_argument("--user", help="UPN or object id of another user (needs Presence.Read.All)")
    args = parser.parse_args()

    client = GraphClient(tenant=tenant).with_username_and_password(client_id, username, password)

    if args.user:
        target = args.user
        presence = client.users[args.user].presence.get()
    else:
        target = "me"
        presence = client.me.presence.get()
    presence.execute_query()

    describe(target, presence)


if __name__ == "__main__":
    main()
