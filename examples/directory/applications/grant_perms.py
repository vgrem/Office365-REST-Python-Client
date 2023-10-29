"""
Grant or revoke API permissions

https://learn.microsoft.com/en-us/graph/permissions-grant-via-msgraph?tabs=http&pivots=grant-application-permissions
"""

from office365.graph_client import GraphClient
from tests import (
    test_admin_principal_name,
    test_client_id,
    test_tenant,
)

client = GraphClient.with_token_interactive(
    test_tenant, test_client_id, test_admin_principal_name
)

# Step 1: Get the appRoles of the resource service principal
resource = (
    client.service_principals.single("displayName eq 'Microsoft Graph'")
    .get()
    .select(["id", "displayName", "appId", "appRoles"])
    .expand(["appRoleAssignedTo"])
    .execute_query()
)

# select specific appRole
app_role = next(
    iter([item for item in resource.app_roles if item.value == "Place.Read.All"])
)


# Step 2: Grant an app role to a client service principal
app_service_principal = client.service_principals.get_by_app_id(test_client_id)
app_service_principal.grant(resource, app_role).execute_query()
