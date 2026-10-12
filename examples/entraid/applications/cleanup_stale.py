"""
Delete app registrations that can no longer authenticate.

An app is considered stale when it has no credentials at all, or every password
and certificate has expired. Such apps cannot obtain tokens, so they are safe
candidates for cleanup.

Usage:

    python cleanup_stale.py            # dry run: only list stale apps
    python cleanup_stale.py --apply     # actually delete them

Requires an interactive sign-in by a Global Administrator or Privileged Role
Administrator (the delegated ``Application.ReadWrite.All`` scope is carried by
the signed-in account).

Reference:
    https://learn.microsoft.com/en-us/graph/api/application-delete
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


def _is_stale(app) -> bool:
    creds = list(app.password_credentials or []) + list(app.key_credentials or [])
    return not creds or all(c.is_expired for c in creds)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="delete stale apps (default: report only)")
    args = parser.parse_args()

    client = _privileged_client()
    deleted = 0

    for app in client.applications.get_all().execute_query():
        if not _is_stale(app):
            continue
        if args.apply:
            app.delete_object().execute_query()
        print(f"  {app.display_name}  (app_id={app.app_id})")
        deleted += 1

    verb = "Deleted" if args.apply else "Would delete"
    print(f"\n{verb} {deleted} stale app(s).")


if __name__ == "__main__":
    main()
