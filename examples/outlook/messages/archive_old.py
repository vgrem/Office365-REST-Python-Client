"""
Archive old messages — move messages older than N days into an "Archive" folder.

A typical retention workflow: find inbox messages past a cutoff and move them to
a dedicated folder (created on first run). Dry-run by default.

Requires delegated permission ``Mail.ReadWrite``.

https://learn.microsoft.com/en-us/graph/api/message-move
"""

from __future__ import annotations

import argparse
from datetime import datetime, timedelta, timezone

from office365.graph_client import GraphClient
from tests.settings import client_id, password, tenant, username


def main() -> None:
    parser = argparse.ArgumentParser(description="Archive messages older than N days")
    parser.add_argument("--days", type=int, default=365, help="age threshold in days (default: 365)")
    parser.add_argument("--folder", default="inbox", help="source folder (default: inbox)")
    parser.add_argument("--apply", action="store_true", help="actually move the messages")
    args = parser.parse_args()

    client = GraphClient(tenant=tenant).with_username_and_password(client_id, username, password)
    folder = client.me.mail_folders[args.folder]

    cutoff = datetime.now(timezone.utc) - timedelta(days=args.days)
    cutoff_literal = cutoff.strftime("%Y-%m-%dT%H:%M:%SZ")
    messages = folder.messages.filter(f"receivedDateTime lt {cutoff_literal}").get().execute_query()
    print(f"Found {len(messages)} message(s) older than {args.days} days")

    if not args.apply:
        for message in list(messages)[:5]:
            print(f"  would archive: {message.subject}")
        print("Dry run — re-run with --apply to archive.")
        return

    archive = folder.child_folders.find_by_display_name("Archive").execute_query()
    if not archive.is_loaded:
        archive = folder.child_folders.add("Archive").execute_query()
        print("Created 'Archive' folder")

    for message in messages:
        message.move(archive.id).execute_query()
    print(f"Moved {len(messages)} message(s) to Archive")


if __name__ == "__main__":
    main()
