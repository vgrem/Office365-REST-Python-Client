"""
Find shared mailboxes in a tenant — by convention, since Graph has no endpoint.

Microsoft Graph has **no** "list shared mailboxes" API: a shared mailbox is just
a user object, and only Exchange Online (``Get-Mailbox -RecipientTypeDetails
SharedMailbox`` / PowerShell) knows for sure. The usual workaround is a naming or
attribute convention; this example scans a page of users and filters on the
``mail``/``userPrincipalName`` containing a token. Treat the result as a
heuristic, not an authority.

Requires delegated or app permission ``User.Read.All``.

https://learn.microsoft.com/en-us/graph/api/resources/shared-mailbox
"""

from __future__ import annotations

import argparse

from office365.graph_client import GraphClient
from tests.settings import client_id, client_secret, tenant


def main() -> None:
    parser = argparse.ArgumentParser(description="Heuristically list shared mailboxes")
    parser.add_argument("--contains", default="shared", help="token to match in the UPN/mail (default: shared)")
    parser.add_argument("--scan", type=int, default=200, help="how many users to scan (default: 200)")
    args = parser.parse_args()

    client = GraphClient(tenant=tenant).with_client_secret(client_id, client_secret)
    users = client.users.select(["id", "displayName", "userPrincipalName", "mail"]).top(args.scan).get().execute_query()

    token = args.contains.lower()
    matches = [u for u in users if token in (u.user_principal_name or "").lower() or token in (u.mail or "").lower()]

    print(f"Users matching '{args.contains}' ({len(matches)} of {len(users)} scanned):")
    for user in matches:
        print(f"  {user.user_principal_name or '':50s}  {user.display_name}")
    print("\nNote: Graph has no shared-mailbox filter — confirm with Exchange Online (Get-Mailbox).")


if __name__ == "__main__":
    main()
