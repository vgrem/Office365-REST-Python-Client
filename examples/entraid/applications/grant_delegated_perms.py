"""
Grant a delegated (OAuth2) scope to an app via admin consent.

Idempotent: if the scope is already granted nothing changes, so it is safe to
re-run. The grant is tenant-wide (``consentType=AllPrincipals``).

Usage:

    python grant_delegated_perms.py --scope User.Read
    python grant_delegated_perms.py --scope Mail.Read --app-id <guid>

Requires an interactive sign-in by a Global Administrator or Privileged Role
Administrator (interactive consent is what makes the tenant-wide grant work).

Reference:
    https://learn.microsoft.com/en-us/graph/permissions-grant-via-msgraph
"""

from __future__ import annotations

import argparse

from office365.graph_client import GraphClient
from tests.settings import admin_username, client_id, tenant


def _privileged_client() -> GraphClient:
    """Sign in interactively with an admin account to grant consent."""
    return (
        GraphClient(tenant=tenant)
        .with_token_interactive(client_id, admin_username)
        .require_role("Global Administrator", "Privileged Role Administrator")
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scope", default="User.Read", help="delegated scope to grant")
    parser.add_argument("--app-id", default=client_id, help="application (client) ID that receives the grant")
    args = parser.parse_args()

    privileged_client = _privileged_client()
    if privileged_client.has_delegated_permission(args.scope, args.app_id):
        print(f"'{args.scope}' is already granted to {args.app_id}.")
        return

    privileged_client.grant_delegated_permissions(args.app_id, args.scope).execute_query()
    print(f"Granted '{args.scope}' to {args.app_id}.")


if __name__ == "__main__":
    main()
