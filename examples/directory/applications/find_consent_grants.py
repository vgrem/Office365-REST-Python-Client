"""
Find consent grants for app permissions
"""

from office365.graph_client import GraphClient
from tests import test_client_id, test_client_secret, test_tenant

client = GraphClient(tenant=test_tenant).with_client_secret(
    test_client_id, test_client_secret
)


col = client.service_principals.get().execute_query()
for sp in col:
    print("--- ", sp.display_name, " ---")

    grants = sp.oauth2_permission_grants.get().execute_query()
    if len(grants) > 0:
        print("Delegated Permissions (User Consent)")
        for grant in grants:
            consent_info = grant.consent_type
            if grant.consent_type != "AllPrincipals":
                user = client.users[grant.principal_id].get().execute_query()
                consent_info += " (" + user.user_principal_name + ")"
            print(consent_info, ": ", grant.scope)

    app_roles = sp.app_role_assignments.get().execute_query()
    if len(app_roles) > 0:
        print("Application Permissions (Admin Consent)")
        for app_role in app_roles:
            resource_sp = (
                client.service_principals[app_role.resource_id].get().execute_query()
            )
            print(app_role.resource_display_name, ": ", resource_sp.app_roles)
