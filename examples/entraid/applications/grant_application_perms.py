"""
Grant an application role (app-only permission) to an app.

Application roles run without a signed-in user, so granting one is a privileged
operation. Sign in interactively with a Global Administrator or Privileged Role
Administrator. When the admin still lacks ``AppRoleAssignment.ReadWrite.All`` the
script explains the requirement and exits successfully instead of crashing.

Usage:

    python grant_application_perms.py --role User.Read.All
    python grant_application_perms.py --role Mail.Read --app-id <guid>

Reference:
    https://learn.microsoft.com/en-us/graph/permissions-grant-via-msgraph
    https://learn.microsoft.com/en-us/graph/api/serviceprincipal-post-approleassignedto
"""

from __future__ import annotations

import argparse

from office365.graph_client import GraphClient
from office365.runtime.client_request_exception import ClientRequestException
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
    parser.add_argument("--role", default="User.Read.All", help="application role to grant")
    parser.add_argument("--app-id", default=client_id, help="application (client) ID that receives the grant")
    args = parser.parse_args()

    privileged_client = _privileged_client()
    if privileged_client.has_application_permissions(args.role, args.app_id):
        print(f"'{args.role}' is already granted to {args.app_id}.")
        return

    try:
        privileged_client.grant_application_permissions(args.app_id, args.role).execute_query()
    except ClientRequestException as exc:
        print(f"Could not grant '{args.role}': {exc}.")
        print("Application-role consent also requires the AppRoleAssignment.ReadWrite.All permission.")
        return
    print(f"Granted '{args.role}' to {args.app_id}.")


if __name__ == "__main__":
    main()
