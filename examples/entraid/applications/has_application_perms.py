"""
Check whether an application role (app-only permission) is granted to an app.

Read-only: prints the answer and exits.

Usage:

    python has_application_perms.py --role User.Read.All
    python has_application_perms.py --role Mail.Read --app-id <guid>

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
    parser.add_argument("--role", default="User.Read.All", help="application role to check")
    parser.add_argument("--app-id", default=client_id, help="application (client) ID to inspect")
    args = parser.parse_args()

    client = _client()
    granted = client.has_application_permissions(args.role, args.app_id)
    print(f"'{args.role}' {'IS' if granted else 'is NOT'} granted to {args.app_id}.")


if __name__ == "__main__":
    main()
