"""
Find messages with large attachments — over a size threshold.

Exchange's ``message`` has no ``size`` property; size lives on the **attachments**.
This expands them, sums the bytes and reports the biggest storage consumers in a
folder, largest first.

Requires delegated permission ``Mail.Read``.

https://learn.microsoft.com/en-us/graph/api/message-list-attachments
"""

from __future__ import annotations

import argparse

from office365.graph_client import GraphClient
from tests.settings import client_id, password, tenant, username


def main() -> None:
    parser = argparse.ArgumentParser(description="Find messages whose attachments exceed a size")
    parser.add_argument("--min-mb", type=float, default=1.0, help="threshold in MB (default: 1)")
    parser.add_argument("--folder", default="inbox", help="mail folder name or id (default: inbox)")
    parser.add_argument("--scan", type=int, default=200, help="how many recent messages to scan (default: 200)")
    args = parser.parse_args()

    min_bytes = int(args.min_mb * 1024 * 1024)
    client = GraphClient(tenant=tenant).with_username_and_password(client_id, username, password)
    messages = (
        client.me.mail_folders[args.folder]
        .messages.filter("hasAttachments eq true")
        .expand(["attachments"])
        .select(["subject", "from", "receivedDateTime"])
        .top(args.scan)
        .get()
        .execute_query()
    )

    rows = []
    for message in messages:
        total = sum(attachment.size or 0 for attachment in message.attachments)
        if total >= min_bytes:
            rows.append((total, message))
    rows.sort(key=lambda row: row[0], reverse=True)

    print(f"Messages with attachments over {args.min_mb:g} MB ({len(rows)}):\n")
    for total, message in rows:
        sender = message.from_recipient.emailAddress.address if message.from_recipient else ""
        print(f"  {total / (1024 * 1024):6.1f} MB  {message.subject or '':40s}  {sender}")


if __name__ == "__main__":
    main()
