"""
Remove superseded client secrets, keeping only the newest on each app.

After rotation the old credential keeps working (that overlap is intentional),
so this is the second half of the rotation: once the new secret is deployed,
delete everything except the most recent password credential.

Usage:

    python cleanup_old.py            # dry run: only list what would be removed
    python cleanup_old.py --apply     # actually remove old secrets

Requires an interactive sign-in by a Global Administrator or Privileged Role
Administrator (the delegated ``Application.ReadWrite.All`` scope is carried by
the signed-in account).

Reference:
    https://learn.microsoft.com/en-us/graph/api/application-removepassword
"""

from __future__ import annotations

import argparse

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
    parser.add_argument("--apply", action="store_true", help="remove old secrets (default: report only)")
    args = parser.parse_args()

    client = _privileged_client()
    removed = 0

    for app in client.applications.get_all().execute_query():
        creds = [c for c in (app.password_credentials or []) if c.keyId]
        if len(creds) <= 1:
            continue
        newest = max(creds, key=lambda c: c.startDateTime or c.endDateTime)
        for cred in creds:
            if cred.keyId is None or cred.keyId == newest.keyId:
                continue
            if args.apply:
                app.remove_password(cred.keyId).execute_query()
            print(f"  {app.display_name:40s}  removed hint={cred.hint}  {cred.endDateTime.date()}")
            removed += 1

    verb = "Removed" if args.apply else "Would remove"
    print(f"\n{verb} {removed} old secret(s) (keeping the newest on each app).")


if __name__ == "__main__":
    main()
