"""
List the delegated (OAuth2) scopes granted to an app.

These are the Microsoft Graph scopes the app can request on behalf of a
signed-in user, as granted by tenant-wide admin consent.

Usage:

    python list_delegated_perms.py                 # this app
    python list_delegated_perms.py --app-id <guid>

Requires application permission ``Directory.Read.All`` (delegated
``DelegatedPermissionGrant.Read.All`` also works).

Reference:
    https://learn.microsoft.com/en-us/graph/api/serviceprincipal-list-delegatedpermissions
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
    scopes = list(client.get_delegated_permissions(args.app_id).execute_query().value)
    print(f"Delegated scopes granted to {args.app_id} ({len(scopes)}):")
    for scope in scopes:
        print(f"  {scope}")


if __name__ == "__main__":
    main()
