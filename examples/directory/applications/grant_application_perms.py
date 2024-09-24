"""
Grant or revoke API permissions

Steps:

1. Register an application with Azure AD
2. Addressing an application or a service principal object
3. Configure other basic properties for your app
4. Limit app sign-in to only assigned identities
5. Assign permissions to an app
6. Create app roles
7. Manage owners

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

# Step 1: Get the resource service principal
resource = client.service_principals.get_by_name("Microsoft Graph")

# Step 2: Grant an app role to a client app
app = client.applications.get_by_app_id(test_client_id)
resource.grant_application_permissions(app, "MailboxSettings.Read").execute_query()


# Step 3. Print app role assignments
result = resource.app_role_assigned_to.get_all().execute_query()
for app_role_assignment in result:
    print(app_role_assignment)
