"""
Read presence for many users in a single request — the cheap way to build a
"who is available right now" view.

``getPresencesByUserId`` accepts up to 650 ids (or UPNs) per call, so an
agent-desktop or a people-picker needs one round trip, not one per user.

Requires the delegated permission ``Presence.Read.All``.

https://learn.microsoft.com/en-us/graph/api/cloudcommunications-getpresencesbyuserid
"""

import argparse

from office365.graph_client import GraphClient
from tests.settings import admin_username, client_id, password, tenant, username


def main():
    parser = argparse.ArgumentParser(description="Bulk-read presence")
    parser.add_argument(
        "--users",
        nargs="+",
        default=[username, admin_username],
        help="UPNs or object ids (up to 650 per request)",
    )
    parser.add_argument(
        "--resolve-names",
        action="store_true",
        help="map object ids back to UPNs (one extra request per user)",
    )
    args = parser.parse_args()

    client = GraphClient(tenant=tenant).with_username_and_password(client_id, username, password)
    presences = client.communications.get_presences_by_user_id(args.users).execute_query()

    print(f"Requested {len(args.users)} user(s), got {len(presences)} presence record(s):\n")
    for presence in presences:
        label = presence.id
        if args.resolve_names:
            user = client.users[presence.id].select(["userPrincipalName"]).get().execute_query()
            label = user.user_principal_name
        print(f"  {label:<45} {str(presence.availability):<16} {presence.activity}")


if __name__ == "__main__":
    main()
