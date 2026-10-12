"""
Revoke a delegated (OAuth2) scope grant from an app.

Useful when a user-specific consent grant blocks creating the tenant-wide
(AllPrincipals) grant: revoke first, then grant again with
``grant_delegated_perms.py``.

Usage:

    python revoke_delegated_perms.py --scope User.Read
    python revoke_delegated_perms.py --scope Mail.Read --app-id <guid>

Requires an interactive sign-in by a Global Administrator or Privileged Role
Administrator.

Reference:
    https://learn.microsoft.com/en-us/graph/api/oauth2permissiongrant-delete
"""

from __future__ import annotations

import argparse

from office365.graph_client import GraphClient
from tests.settings import admin_username, client_id, tenant


def _privileged_client() -> GraphClient:
    """Sign in interactively with an admin account to manage consent."""
    return (
        GraphClient(tenant=tenant)
        .with_token_interactive(client_id, admin_username)
        .require_role("Global Administrator", "Privileged Role Administrator")
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scope", default="User.Read", help="delegated scope to revoke")
    parser.add_argument("--app-id", default=client_id, help="application (client) ID whose grant is revoked")
    args = parser.parse_args()

    privileged_client = _privileged_client()
    privileged_client.revoke_delegated_permissions(args.app_id, args.scope).execute_query()
    print(f"Revoked '{args.scope}' from {args.app_id}.")


if __name__ == "__main__":
    main()
