"""
Grant or revoke API permissions

https://learn.microsoft.com/en-us/graph/permissions-grant-via-msgraph?tabs=http&pivots=grant-application-permissions
"""

from office365.graph_client import GraphClient
from tests.graph_case import acquire_token_by_username_password

client = GraphClient(acquire_token_by_username_password)

# Step 1: Get the appRoles of the resource service principal
service_principal = client.service_principals.filter("displayName eq 'Microsoft Graph'").single().get().execute_query()
# Step 2: Grant an app role to a client service principal
