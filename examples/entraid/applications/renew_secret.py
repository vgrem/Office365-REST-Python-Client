"""
Renew an app's client secret *only if* it is expiring soon.

Unlike ``rotate_secret.py`` (which always adds a secret), this checks the newest
password credential first and exits without changes when there is still plenty
of time. Handy as a scheduled hygiene job.

Usage:

    python renew_secret.py                    # renew this app when below 30 days
    python renew_secret.py --warn-days 45
    python renew_secret.py --app-id <guid>

Requires an interactive sign-in by a Global Administrator or Privileged Role
Administrator (the delegated ``Application.ReadWrite.All`` scope is carried by
the signed-in account).

Reference:
    https://learn.microsoft.com/en-us/graph/api/application-addpassword
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone

from office365.graph_client import GraphClient
from tests.settings import admin_username, client_id, tenant

DEFAULT_WARN_DAYS = 30


def _privileged_client() -> GraphClient:
    return (
        GraphClient(tenant=tenant)
        .with_token_interactive(client_id, admin_username)
        .require_role("Global Administrator", "Privileged Role Administrator")
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--app-id", default=client_id, help="application (client) ID to check")
    parser.add_argument("--warn-days", type=int, default=DEFAULT_WARN_DAYS)
    args = parser.parse_args()

    client = _privileged_client()
    app = client.applications.get_by_app_id(args.app_id).get().execute_query()
    passwords = app.password_credentials

    if not passwords:
        secret = app.add_password("Initial secret").execute_query().value
        print(f"No secrets found — created one (keyId={secret.keyId}).")
        print(f"\nCLIENT_SECRET={secret.secretText}")
        return

    newest = max(passwords, key=lambda p: p.days_until_expiry if p.days_until_expiry is not None else 1 << 30)
    days = newest.days_until_expiry
    if days is None or days > args.warn_days:
        print(f"Newest secret expires in {days} days — nothing to do.")
        return

    secret = app.add_password(f"Rotated {datetime.now(timezone.utc):%Y-%m-%d}").execute_query().value
    print(f"Newest secret expires in {days} days — added a replacement (keyId={secret.keyId}).")
    print(f"\nCLIENT_SECRET={secret.secretText}")


if __name__ == "__main__":
    main()
