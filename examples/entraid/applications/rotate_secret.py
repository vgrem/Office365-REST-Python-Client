"""
Add a new client secret to an app (rotate its password credential).

Adding a secret is additive: the old secret keeps working until you remove it
(see ``cleanup_old.py``). That overlap is what makes zero-downtime rotation
possible — deploy the new secret first, then delete the old one.

Usage:

    python rotate_secret.py                       # rotate this app
    python rotate_secret.py --app-id <guid>       # rotate another app

Requires an interactive sign-in by a Global Administrator or Privileged Role
Administrator (the delegated ``Application.ReadWrite.All`` scope is carried by
the signed-in account).

Reference:
    https://learn.microsoft.com/en-us/graph/api/application-addpassword
    https://learn.microsoft.com/en-us/entra/identity-platform/how-to-add-credentials
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone

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
    parser.add_argument("--app-id", default=client_id, help="application (client) ID to rotate")
    args = parser.parse_args()

    client = _privileged_client()
    app = client.applications.get_by_app_id(args.app_id).get().execute_query()

    secret = app.add_password(f"Rotated {datetime.now(timezone.utc):%Y-%m-%d}").execute_query().value
    print(f"Added a secret to {app.display_name} (keyId={secret.keyId}).")
    print(f"\nCLIENT_SECRET={secret.secretText}")
    print("Store it now — Graph never returns the value again.")


if __name__ == "__main__":
    main()
