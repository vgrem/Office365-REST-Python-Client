"""
Send an email **as** a shared mailbox (the From address is the shared mailbox).

The signed-in identity needs *Send As* rights on the shared mailbox (an Exchange
Online admin action). Sending through the mailbox's own ``sendMail`` endpoint
makes the From header the shared mailbox address, not the sender's.

Requires delegated ``Mail.Send.Shared`` (or app ``Mail.Send``).

https://learn.microsoft.com/en-us/graph/api/user-sendmail
"""

from __future__ import annotations

import argparse

from office365.graph_client import GraphClient
from tests.settings import client_id, password, tenant, user_principal, username


def main() -> None:
    parser = argparse.ArgumentParser(description="Send mail as a shared mailbox")
    parser.add_argument("--mailbox", required=True, help="shared mailbox UPN, e.g. support@contoso.com")
    parser.add_argument("--to", action="append", default=[], help="recipient (repeatable; default: the test user)")
    parser.add_argument("--send", action="store_true", help="actually send (otherwise just report the plan)")
    args = parser.parse_args()

    recipients = args.to or [user_principal]
    if not args.send:
        print(f"Would send from {args.mailbox} to {', '.join(recipients)}; re-run with --send.")
        return

    client = GraphClient(tenant=tenant).with_username_and_password(client_id, username, password)
    client.users[args.mailbox].send_mail(
        subject="Sent from a shared mailbox",
        body="This message was sent via office365-rest-python-client.",
        to_recipients=recipients,
    ).execute_query()
    print(f"Email sent from {args.mailbox} to {', '.join(recipients)}.")


if __name__ == "__main__":
    main()
