"""
Report the API permissions an application requests and has been granted.

This answers the recurring governance question *"what can this app do?"* by
combining the views of the same app registration:

* **requested** — the ``requiredResourceAccess`` entries declared in the app
  manifest (what the app asks for at sign-in), resolved per resource;
* **granted delegated** — admin-consented Microsoft Graph OAuth scopes
  (``oauth2PermissionGrants`` with ``consentType=AllPrincipals``);
* **granted application** — Microsoft Graph app roles assigned to the app's
  service principal (``appRoleAssignments``), i.e. permissions that run without
  a signed-in user.

Permission *ids* are resolved to friendly names using each resource's service
principal (``oauth2PermissionScopes`` and ``appRoles``).

Usage:

    python permissions_report.py                       # inspect this app
    python permissions_report.py --app-id <guid>       # inspect another app

Requires application permission ``Directory.Read.All`` (delegated
``Application.Read.All`` + ``DelegatedPermissionGrant.Read.All`` also work).

Reference:
    https://learn.microsoft.com/en-us/graph/api/application-list
    https://learn.microsoft.com/en-us/graph/api/serviceprincipal-list-delegatedpermissions
    https://learn.microsoft.com/en-us/graph/api/serviceprincipal-list-approleassignments
"""

from __future__ import annotations

import argparse

from office365.directory.applications.application import Application
from office365.graph_client import GraphClient
from tests.settings import client_id, client_secret, tenant


def _client() -> GraphClient:
    return GraphClient(tenant=tenant).with_client_secret(client_id, client_secret)


def _requested_permissions(client: GraphClient, app: Application) -> list[str]:
    """Resolve ``requiredResourceAccess`` entries to ``[kind] resource: name``."""
    result: list[str] = []
    resolved: dict[str, tuple[dict[str, str], dict[str, str], str]] = {}
    for entry in app.required_resource_access:
        resource_id = entry.resourceAppId or ""
        if resource_id not in resolved:
            sp = (
                client.service_principals.get_by_app_id(resource_id)
                .select(["displayName", "oauth2PermissionScopes", "appRoles"])
                .get()
                .execute_query()
            )
            scopes = {s.id: s.value for s in sp.oauth2_permission_scopes if s.id}
            roles = {r.id: r.value for r in sp.app_roles if r.id}
            resolved[resource_id] = (scopes, roles, sp.display_name or resource_id)
        scopes, roles, resource_name = resolved[resource_id]
        for access in entry.resourceAccess:
            delegated = access.type == "Scope"
            name = (scopes if delegated else roles).get(access.id or "", access.id or "?")
            kind = "delegated" if delegated else "application"
            result.append(f"[{kind}] {resource_name}: {name}")
    return result


def _print_permissions(title: str, names: list[str]) -> None:
    print(f"\n{title}")
    if names:
        for name in names:
            print(f"  {name}")
    else:
        print("  (none)")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--app-id", default=client_id, help="Application (client) ID to inspect")
    args = parser.parse_args()

    client = _client()
    app = client.applications.get_by_app_id(args.app_id).get().execute_query()
    print(f"{app.display_name} (appId={app.app_id})")
    _print_permissions("Requested (requiredResourceAccess):", _requested_permissions(client, app))

    principals = list(client.service_principals.filter(f"appId eq '{args.app_id}'").select(["id"]).get().execute_query())
    if not principals:
        print("\nNo service principal exists yet — the app has not been consented and holds no grants.")
        return

    delegated = list(client.get_delegated_permissions(args.app_id).execute_query().value)
    application = [role.value for role in client.get_application_permissions(args.app_id).execute_query().value]
    _print_permissions("Granted delegated Microsoft Graph permissions (admin consent):", delegated)
    _print_permissions("Granted application Microsoft Graph permissions (no signed-in user):", application)


if __name__ == "__main__":
    main()
