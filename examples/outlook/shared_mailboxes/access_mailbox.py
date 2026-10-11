"""
Access a shared mailbox you don't own: read its recent messages and folders.

The key pattern: a shared mailbox is exposed as an ordinary user object, so you
address it with ``client.users[<shared-mailbox-upn>]`` instead of ``client.me``.
Your identity needs access (delegated) or ``Mail.Read`` (app).

Requires delegated ``Mail.Read.Shared`` (or app ``Mail.Read``).

https://learn.microsoft.com/en-us/graph/api/resources/shared-mailbox
"""

from __future__ import annotations

import argparse

from office365.graph_client import GraphClient
from tests.settings import client_id, password, tenant, username


def main() -> None:
    parser = argparse.ArgumentParser(description="Read a shared mailbox")
    parser.add_argument("--mailbox", required=True, help="shared mailbox UPN, e.g. support@contoso.com")
    parser.add_argument("--top", type=int, default=5, help="how many messages to show (default: 5)")
    args = parser.parse_args()

    client = GraphClient(tenant=tenant).with_username_and_password(client_id, username, password)
    shared = client.users[args.mailbox]

    messages = shared.messages.top(args.top).get().execute_query()
    print(f"Recent messages in {args.mailbox} ({len(messages)}):\n")
    for message in messages:
        print(f"  {message.subject or '(no subject)'}")

    folders = shared.mail_folders.get().execute_query()
    print(f"\nFolders ({len(folders)}):")
    for folder in folders:
        print(f"  {folder.display_name}")


if __name__ == "__main__":
    main()
