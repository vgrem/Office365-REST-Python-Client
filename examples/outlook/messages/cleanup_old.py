"""
Clean up old messages — dry-run, then delete.

Finds messages older than N days in a folder and, with ``--apply``, deletes them.
Dry-run by default, so it is safe to try.

Requires delegated permission ``Mail.ReadWrite``.

https://learn.microsoft.com/en-us/graph/api/message-delete
"""

from __future__ import annotations

import argparse
from datetime import datetime, timedelta, timezone

from office365.graph_client import GraphClient
from tests.settings import client_id, password, tenant, username

PREVIEW_LIMIT = 5


def main() -> None:
    parser = argparse.ArgumentParser(description="Delete messages older than N days (dry-run unless --apply)")
    parser.add_argument("--days", type=int, default=180, help="age threshold in days (default: 180)")
    parser.add_argument("--folder", default="inbox", help="mail folder name or id (default: inbox)")
    parser.add_argument("--apply", action="store_true", help="actually delete the messages")
    args = parser.parse_args()

    client = GraphClient(tenant=tenant).with_username_and_password(client_id, username, password)
    folder = client.me.mail_folders[args.folder]

    cutoff = datetime.now(timezone.utc) - timedelta(days=args.days)
    cutoff_literal = cutoff.strftime("%Y-%m-%dT%H:%M:%SZ")
    messages = folder.messages.filter(f"receivedDateTime lt {cutoff_literal}").get().execute_query()
    print(f"Found {len(messages)} message(s) older than {args.days} days")

    if not args.apply:
        for message in list(messages)[:PREVIEW_LIMIT]:
            print(f"  {message.subject or '':40s}  {message.received_date_time}")
        if len(messages) > PREVIEW_LIMIT:
            print(f"  ... and {len(messages) - PREVIEW_LIMIT} more")
        print("Dry run — re-run with --apply to delete.")
        return

    for message in messages:
        message.delete_object().execute_query()
    print(f"Deleted {len(messages)} message(s)")


if __name__ == "__main__":
    main()
