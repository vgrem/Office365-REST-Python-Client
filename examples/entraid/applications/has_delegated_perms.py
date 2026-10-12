"""
Check whether a delegated (OAuth2) scope is granted to an app.

Read-only: prints the answer and exits. Combine with ``grant_delegated_perms.py``
to make a permission pipeline idempotent.

Usage:

    python has_delegated_perms.py --scope User.Read
    python has_delegated_perms.py --scope Mail.Read --app-id <guid>

Requires application permission ``Directory.Read.All`` (delegated
``DelegatedPermissionGrant.Read.All`` also works).

Reference:
    https://learn.microsoft.com/en-us/graph/permissions-grant-via-msgraph
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
    parser.add_argument("--scope", default="User.Read", help="delegated scope to check")
    parser.add_argument("--app-id", default=client_id, help="application (client) ID to inspect")
    args = parser.parse_args()

    client = _client()
    if client.has_delegated_permission(args.scope, args.app_id):
        print(f"'{args.scope}' IS granted to {args.app_id}.")
    else:
        print(f"'{args.scope}' is NOT granted to {args.app_id}.")


if __name__ == "__main__":
    main()
