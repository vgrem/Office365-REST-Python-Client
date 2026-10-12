"""
Review OAuth consent grants — which apps have user-consented permissions
to access tenant data.

OAuth consent grants allow applications to act on behalf of users.
Unreviewed grants are a common source of shadow IT and data exposure.
This script lists all delegated permission grants for review.

Inspired by FindAppConsentGrants.PS1 and Report-PermissionConsentRequests.PS1
from Office 365 for IT Pros.

Required delegated permissions:
    DelegatedPermissionGrant.Read.All   Read consent grants

https://learn.microsoft.com/en-us/graph/api/resources/oauth2permissiongrant
"""

from office365.graph_client import GraphClient
from tests.settings import client_id, client_secret, tenant


def list_consent_grants() -> list[dict]:
    """List all OAuth consent grants (delegated permissions) in the tenant.

    Returns list of consent grant dicts sorted by app name.
    """
    client = GraphClient(tenant=tenant).with_client_secret(client_id, client_secret)

    grants = []
    try:
        oauth_grants = client.oauth2_permission_grants.get().execute_query()
        for g in oauth_grants:
            client_app = getattr(g, "client_id", "Unknown")
            scope = getattr(g, "scope", "")
            consent_type = getattr(g, "consent_type", "AllPrincipals")

            # Resolve app name from service principal
            app_name = client_app
            try:
                sp = client.service_principals[client_app].select(["displayName"]).get().execute_query()
                app_name = getattr(sp, "display_name", client_app)
            except Exception:
                pass

            grants.append(
                {
                    "app": app_name,
                    "app_id": client_app,
                    "scope": scope,
                    "consent_type": consent_type,
                }
            )
    except Exception as e:
        print(f"  Warning: could not fetch consent grants: {e}")

    grants.sort(key=lambda x: x["app"].lower())
    return grants


def main():
    print("OAuth consent grant review\n")
    grants = list_consent_grants()

    if not grants:
        print("No consent grants found.")
        return

    print(f"Found {len(grants)} consent grants:\n")
    print(f"{'App':40s} {'Scope (+ client)':40s} {'Type'}")
    print("-" * 90)
    for g in grants:
        app = g["app"][:38]
        scope = g["scope"][:38]
        print(f"{app:40s} {scope:40s} {g['consent_type']}")

    admin_consent = [g for g in grants if g["consent_type"] == "AllPrincipals"]
    user_consent = [g for g in grants if g["consent_type"] != "AllPrincipals"]

    print()
    print(f"Admin-consented (all users):  {len(admin_consent)}")
    print(f"User-consented (individual):  {len(user_consent)}")

    if user_consent:
        print("\n⚠️  User-consented grants need individual review — each represents")
        print("   a user authorizing an app to access their data.")


if __name__ == "__main__":
    main()
