"""
Revoke delegated permissions granted to a service principal on behalf of a user

https://learn.microsoft.com/en-us/graph/permissions-grant-via-msgraph?tabs=http&pivots=grant-delegated-permissions#step-3-revoke-delegated-permissions-granted-to-a-service-principal-on-behalf-of-a-user-optional
"""

from office365.graph_client import GraphClient
from tests import (
    test_admin_principal_name,
    test_client_id,
    test_tenant,
    test_user_principal_name,
)

client = GraphClient.with_token_interactive(
    test_tenant, test_client_id, test_admin_principal_name
)

# Step 1: Get resource service principal
resource = client.service_principals.get_by_name("Microsoft Graph")
user = client.users.get_by_principal_name(test_user_principal_name)
resource.revoke_delegated_permissions(test_client_id, user, "User.Read.All").execute_query()
