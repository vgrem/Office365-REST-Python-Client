"""
Revoke an application role (app-only permission) from an app.

Usage:

    python revoke_application_perms.py --role Mail.Read
    python revoke_application_perms.py --role User.Read.All --app-id <guid>

Requires an interactive sign-in by a Global Administrator or Privileged Role
Administrator with ``AppRoleAssignment.ReadWrite.All``.

Reference:
    https://learn.microsoft.com/en-us/graph/api/serviceprincipal-delete-approleassignedto
"""

from __future__ import annotations

import argparse

from office365.graph_client import GraphClient
from office365.runtime.client_request_exception import ClientRequestException
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
    parser.add_argument("--role", default="Mail.Read", help="application role to revoke")
    parser.add_argument("--app-id", default=client_id, help="application (client) ID whose grant is revoked")
    args = parser.parse_args()

    privileged_client = _privileged_client()
    try:
        privileged_client.revoke_application_permissions(args.app_id, args.role).execute_query()
    except ClientRequestException as exc:
        print(f"Could not revoke '{args.role}': {exc}.")
        print("Application-role consent also requires the AppRoleAssignment.ReadWrite.All permission.")
        return
    print(f"Revoked '{args.role}' from {args.app_id}.")


if __name__ == "__main__":
    main()
