"""
Grant an app (service principal) access to one specific SharePoint site.

This is the "Sites.Selected" pattern: instead of tenant-wide ``Sites.*`` consent,
an app is granted the ``Sites.Selected`` application role and then explicitly
given read or write access to individual sites.

Usage:

    python grant_site_selected_permission.py --role write
    python grant_site_selected_permission.py --site https://contoso.sharepoint.com/sites/team --app-id <guid>

Requires an interactive sign-in by a SharePoint Administrator or Global
Administrator (the target app must already hold the ``Sites.Selected``
application role).

Reference:
    https://learn.microsoft.com/en-us/graph/api/site-post-permissions
"""

from __future__ import annotations

import argparse

from office365.graph_client import GraphClient
from tests.settings import admin_username, client_id, team_site_url, tenant


def _privileged_client() -> GraphClient:
    """Sign in interactively with a SharePoint/Global admin to grant site access."""
    return GraphClient(tenant=tenant).with_token_interactive(client_id, admin_username)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--site", default=team_site_url, help="target site URL")
    parser.add_argument("--app-id", default=client_id, help="application (client) ID to grant")
    parser.add_argument("--role", default="write", choices=["read", "write", "manage", "fullcontrol"])
    args = parser.parse_args()

    if not args.site:
        parser.error("--site is required (set OFFICE365_TEAM_SITE_URL or pass it explicitly)")

    privileged_client = _privileged_client()
    site = privileged_client.sites.get_by_url(args.site).execute_query()
    permission = site.grant_app_access(args.app_id, args.role).execute_query()
    print(f"Granted {permission.roles} to app {args.app_id} on {args.site}")


if __name__ == "__main__":
    main()
