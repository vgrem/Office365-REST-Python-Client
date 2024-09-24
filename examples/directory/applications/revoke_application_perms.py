"""
Revoke an app role assignment from a client service principal

https://learn.microsoft.com/en-us/graph/permissions-grant-via-msgraph?tabs=http&pivots=grant-application-permissions
"""

from office365.graph_client import GraphClient
from tests import (
    test_admin_principal_name,
    test_client_id,
    test_password,
    test_tenant,
    test_username,
)

# client = GraphClient.with_token_interactive(
#    test_tenant, test_client_id, test_admin_principal_name
# )

client = GraphClient.with_username_and_password(
    test_tenant, test_client_id, test_username, test_password
)


# Get resource
resource = client.service_principals.get_by_name("Microsoft Graph")
resource.revoke_application_permissions(test_client_id, "MailboxSettings.Read").execute_query()
