"""
Export messages from a folder to CSV — subject, sender, date, attachments.

For audit, backup or offline analysis of a mailbox. ``message`` has no ``size``
property in Exchange, so this exports what the server does expose.

Requires delegated permission ``Mail.Read``.

https://learn.microsoft.com/en-us/graph/api/user-list-messages
"""

from __future__ import annotations

import argparse
import csv
import tempfile
from pathlib import Path

from office365.graph_client import GraphClient
from tests.settings import client_id, password, tenant, username


def main() -> None:
    parser = argparse.ArgumentParser(description="Export a mail folder to CSV")
    parser.add_argument("--folder", default="inbox", help="mail folder name or id (default: inbox)")
    parser.add_argument("--output", default=str(Path(tempfile.gettempdir()) / "mail_export.csv"), help="CSV output path")
    args = parser.parse_args()

    client = GraphClient(tenant=tenant).with_username_and_password(client_id, username, password)
    folder = client.me.mail_folders[args.folder]
    messages = folder.messages.select(["subject", "from", "receivedDateTime", "hasAttachments"]).get().execute_query()

    with open(args.output, "w", newline="", encoding="utf-8") as stream:
        writer = csv.writer(stream)
        writer.writerow(["Subject", "From", "Received", "Has attachments"])
        for message in messages:
            sender = message.from_recipient.emailAddress.address if message.from_recipient else ""
            writer.writerow([message.subject or "", sender, message.received_date_time, message.has_attachments])

    print(f"Exported {len(messages)} message(s) to {args.output}")


if __name__ == "__main__":
    main()
