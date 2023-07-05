"""
Grant or revoke API permissions

https://learn.microsoft.com/en-us/graph/permissions-grant-via-msgraph?tabs=http&pivots=grant-application-permissions
"""

from office365.graph_client import GraphClient
from tests.graph_case import acquire_token_by_username_password

client = GraphClient(acquire_token_by_username_password)

# Step 1: Get the appRoles of the resource service principal
service_principal = client.service_principals.single("displayName eq 'Microsoft Graph'").get().execute_query()
print(service_principal.id)
# Step 2: Grant an app role to a client service principal
