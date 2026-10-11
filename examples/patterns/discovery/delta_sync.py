"""
Delta query — track changes to files and folders, and resume with a token.

The recommended way to keep a local cache in sync: run a full delta, store the
returned delta token, then on the next run resume from that token to fetch only
what changed since.

Requires delegated permission ``Files.Read``.

https://learn.microsoft.com/en-us/graph/api/driveitem-delta
"""

import argparse

from office365.graph_client import GraphClient
from tests.settings import client_id, password, tenant, username


def _tag(item):
    if item.deleted:
        return "deleted"
    created = item.created_date_time
    modified = item.last_modified_date_time
    if created and modified and created == modified:
        return "new"
    return "updated"


def main():
    parser = argparse.ArgumentParser(description="Track file changes with delta query")
    parser.add_argument("--token", help="resume from a previously stored delta token")
    args = parser.parse_args()

    client = GraphClient(tenant=tenant).with_username_and_password(client_id, username, password)
    query = client.me.drive.root.delta
    if args.token:
        query = query.token(args.token)
        print("Resuming from stored token...\n")
    else:
        print("Initial delta (full sync)...\n")

    changes = query.get_all().execute_query()
    print(f"Changes ({len(changes)}):")
    for item in changes:
        print(f"  [{_tag(item):7s}]  {item.name}")

    token = changes.delta_token
    if token:
        print(f"\nStore this token to resume next time:\n  {token}")
    else:
        print("\nNo delta token returned (no changes to track).")


if __name__ == "__main__":
    main()
