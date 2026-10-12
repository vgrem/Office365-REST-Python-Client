"""
Register a new application (app registration).

Creates a new application with a display name and sign-in audience.
The returned app object includes the app/client ID needed for authentication.

By default the demo app is deleted again (clean run). Pass ``--keep`` to register
a persistent app and print a ready ``OFFICE365_CLIENT_ID=...`` line.

Requires an interactive sign-in by a Global Administrator or Privileged Role
Administrator (the delegated ``Application.ReadWrite.All`` scope is carried by
the signed-in account).

Reference:
    https://learn.microsoft.com/en-us/graph/api/application-post-applications
    https://learn.microsoft.com/en-us/graph/api/resources/application
"""

from __future__ import annotations

import argparse

from office365.graph_client import GraphClient
from tests import create_unique_name
from tests.settings import admin_username, client_id, tenant


def _privileged_client() -> GraphClient:
    """Sign in interactively with an admin account to register an app."""
    return (
        GraphClient(tenant=tenant)
        .with_token_interactive(client_id, admin_username)
        .require_role("Global Administrator", "Privileged Role Administrator")
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--name", help="display name (default: DemoApp + random suffix)")
    parser.add_argument("--keep", action="store_true", help="keep the app instead of deleting it")
    args = parser.parse_args()

    client = _privileged_client()

    app = client.applications.add(
        args.name or create_unique_name("DemoApp"),
        signInAudience="AzureADMyOrg",
    ).execute_query()
    print(f"App created: {app.display_name} (appId: {app.app_id})")

    if args.keep:
        print()
        print("Add to .env:")
        print(f"OFFICE365_CLIENT_ID={app.app_id}")
    else:
        app.delete_object(True).execute_query()
        print("App cleaned up.")


if __name__ == "__main__":
    main()
