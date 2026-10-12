"""
Restore a soft-deleted application and give it a fresh secret.

Deleting an app *without* permanent delete moves it to the deleted-items
container for 30 days. Restoration brings the app back, but credentials and
permissions are NOT preserved, so a new secret is added here.

Usage:

    python restore_app.py --app-id <guid>

Requires an interactive sign-in by a Global Administrator or Privileged Role
Administrator (the delegated ``Application.ReadWrite.All`` scope is carried by
the signed-in account).

Reference:
    https://learn.microsoft.com/en-us/graph/api/directory-deleteditems-list
    https://learn.microsoft.com/en-us/graph/api/directory-deleteditems-restore
"""

from __future__ import annotations

import argparse
import sys

from office365.graph_client import GraphClient
from tests.settings import admin_username, client_id, tenant


def _privileged_client() -> GraphClient:
    return (
        GraphClient(tenant=tenant)
        .with_token_interactive(client_id, admin_username)
        .require_role("Global Administrator", "Privileged Role Administrator")
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--app-id", default=client_id, help="application (client) ID to restore")
    args = parser.parse_args()

    client = _privileged_client()
    deleted_apps = list(client.directory.deleted_applications.get().execute_query())
    target = next((a for a in deleted_apps if a.properties.get("appId") == args.app_id), None)

    if not target:
        print(f"Deleted app with appId '{args.app_id}' not found. Available:")
        for a in deleted_apps:
            print(f"  {a.properties.get('displayName', '?')}  appId={a.properties.get('appId', '?')}")
        sys.exit(1)

    print(f"Found: {target.properties.get('displayName')}")
    target.restore().execute_query()
    print("Restored.")

    app = client.applications.get_by_app_id(args.app_id).get().execute_query()
    secret = app.add_password("Restored secret").execute_query().value
    print(f"New secret created (keyId={secret.keyId}).")
    print(f"\nCLIENT_SECRET={secret.secretText}")


if __name__ == "__main__":
    main()
