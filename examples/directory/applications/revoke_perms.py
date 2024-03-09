"""
Grant or revoke API permissions

https://learn.microsoft.com/en-us/graph/permissions-grant-via-msgraph?tabs=http&pivots=grant-application-permissions
"""

from office365.graph_client import GraphClient
from tests import test_admin_principal_name, test_client_id, test_tenant

client = GraphClient.with_token_interactive(
    test_tenant, test_client_id, test_admin_principal_name
)

# Step 1: Get the appRoles of the resource service principal
resource = (
    client.service_principals.get_by_name("Microsoft Graph")
    .get()
    .select(["id", "displayName", "appId", "appRoles"])
    .execute_query()
)


# Step 2: Revoke an app role assignment from a client service principal
resource.revoke(test_client_id, "Place.Read.All").execute_query()
