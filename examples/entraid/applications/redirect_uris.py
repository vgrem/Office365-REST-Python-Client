"""
Add a redirect URI to an application's web platform.

One of the most common post-registration changes: wiring an app up to a local
development callback or a deployed endpoint.

Usage:

    python redirect_uris.py --uri https://localhost:3000/callback
    python redirect_uris.py --app-id <guid> --uri https://app.contoso.com/signin-oidc

Requires an interactive sign-in by a Global Administrator or Privileged Role
Administrator (the delegated ``Application.ReadWrite.All`` scope is carried by
the signed-in account).

Reference:
    https://learn.microsoft.com/en-us/graph/api/application-update
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
    parser.add_argument("--uri", default="https://localhost:3000/callback", help="redirect URI to add")
    parser.add_argument("--app-id", default=client_id, help="application (client) ID to update")
    args = parser.parse_args()

    client = _privileged_client()
    app = client.applications.get_by_app_id(args.app_id).get().execute_query()

    web = dict(app.properties.get("web") or {})
    uris = list(web.get("redirectUris") or [])
    if args.uri in uris:
        print(f"Redirect URI already present: {args.uri}")
        return

    uris.append(args.uri)
    web["redirectUris"] = uris
    app.set_property("web", web)
    app.update().execute_query()
    print(f"Added redirect URI: {args.uri}")


if __name__ == "__main__":
    main()
