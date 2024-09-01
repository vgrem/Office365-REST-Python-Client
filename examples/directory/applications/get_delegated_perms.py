"""
Retrieves the delegated permissions defined by the Microsoft Graph service principal in the tenant.

https://learn.microsoft.com/en-us/graph/permissions-grant-via-msgraph?tabs=http&pivots=grant-delegated-permissions
"""

from office365.graph_client import GraphClient
from tests import (
    test_client_id,
    test_password,
    test_tenant,
    test_username,
)

client = GraphClient.with_username_and_password(
    test_tenant, test_client_id, test_username, test_password
)
result = (
    client.service_principals.single("displayName eq 'Microsoft Graph'")
    .select(["id", "displayName", "appId", "oauth2PermissionScopes"])
    .get()
    .execute_query()
)
print(result.oauth2_permission_scopes)
