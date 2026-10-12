"""
List the application roles (app-only permissions) granted to an app.

These are the Microsoft Graph permissions that run without a signed-in user.

Usage:

    python list_application_perms.py                 # this app
    python list_application_perms.py --app-id <guid>

Requires application permission ``Directory.Read.All``.

Reference:
    https://learn.microsoft.com/en-us/graph/api/serviceprincipal-list-approleassignments
"""

from __future__ import annotations

import argparse

from office365.graph_client import GraphClient
from tests.settings import client_id, client_secret, tenant


def _client() -> GraphClient:
    return (
        GraphClient(tenant=tenant)
        .with_client_secret(client_id, client_secret)
        .require_application_permission("Directory.Read.All")
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--app-id", default=client_id, help="application (client) ID to inspect")
    args = parser.parse_args()

    client = _client()
    roles = [role.value for role in client.get_application_permissions(args.app_id).execute_query().value]
    print(f"Application roles granted to {args.app_id} ({len(roles)}):")
    for role in roles:
        print(f"  {role}")


if __name__ == "__main__":
    main()
