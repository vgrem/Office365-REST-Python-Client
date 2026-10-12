"""
Rotate every app whose client secret has already expired.

Scans all app registrations and, for each one whose password credential is past
its end date, adds a fresh secret. Useful to recover tenants that were locked
out by the ``AADSTS7000222`` error.

Usage:

    python rotate_all_expired.py            # dry run: only list affected apps
    python rotate_all_expired.py --apply     # actually add replacement secrets

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


def _privileged_client() -> GraphClient:
    return (
        GraphClient(tenant=tenant)
        .with_token_interactive(client_id, admin_username)
        .require_role("Global Administrator", "Privileged Role Administrator")
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="add replacement secrets (default: report only)")
    args = parser.parse_args()

    client = _privileged_client()
    affected = 0

    for app in client.applications.get_all().execute_query():
        expired = [c for c in (app.password_credentials or []) if c.is_expired]
        if not expired:
            continue
        affected += 1
        if not args.apply:
            print(f"  {app.display_name:40s}  expired hint={expired[0].hint}")
            continue
        secret = app.add_password(f"Rotated {datetime.now(timezone.utc):%Y-%m-%d}").execute_query().value
        print(f"  {app.display_name:40s}  old hint={expired[0].hint}  new keyId={secret.keyId}")

    verb = "Rotated" if args.apply else "Found"
    print(f"\n{verb} {affected} app(s) with expired secrets.")


if __name__ == "__main__":
    main()
