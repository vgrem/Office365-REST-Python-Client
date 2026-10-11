"""
Paginate through all messages in a folder with ``$top`` + ``$skip``.

When a mailbox has thousands of messages you page through them explicitly — this
walks the folder one page at a time and counts what it finds. For most cases the
automatic paging of a bare ``get().execute_query()`` (or ``get_all()``) is
enough; use ``$top``/``$skip`` when you need a specific window.

Requires delegated permission ``Mail.Read``.

https://learn.microsoft.com/en-us/graph/api/user-list-messages
"""

from __future__ import annotations

import argparse

from office365.graph_client import GraphClient
from tests.settings import client_id, password, tenant, username


def main() -> None:
    parser = argparse.ArgumentParser(description="Page through a mail folder with $top/$skip")
    parser.add_argument("--folder", default="inbox", help="mail folder name or id (default: inbox)")
    parser.add_argument("--page-size", type=int, default=50, help="messages per page (default: 50)")
    args = parser.parse_args()

    client = GraphClient(tenant=tenant).with_username_and_password(client_id, username, password)
    folder = client.me.mail_folders[args.folder]

    total = 0
    skip = 0
    while True:
        batch = (
            folder.messages.top(args.page_size).skip(skip).select(["subject", "receivedDateTime"]).get().execute_query()
        )
        if len(batch) == 0:
            break
        for message in batch:
            print(f"  {message.received_date_time}  {message.subject}")
        total += len(batch)
        skip += args.page_size

    print(f"\nTotal messages in '{args.folder}': {total}")


if __name__ == "__main__":
    main()
