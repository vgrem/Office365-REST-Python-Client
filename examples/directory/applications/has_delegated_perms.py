"""
Determines whether the delegated permissions is defined by the Microsoft Graph service principal in the tenant.

https://learn.microsoft.com/en-us/graph/permissions-grant-via-msgraph?tabs=http&pivots=grant-delegated-permissions
"""

from office365.graph_client import GraphClient
from tests import (
    test_admin_principal_name,
    test_client_id,
    test_tenant,
)

# client = GraphClient.with_username_and_password(
#    test_tenant, test_client_id, test_username, test_password
# )
client = GraphClient.with_token_interactive(
    test_tenant, test_client_id, test_admin_principal_name
)

resource = client.service_principals.get_by_name("Microsoft Graph")
# app_role = "User.Read.All"
app_role = "BackupRestore-Control.Read.All"
user = client.users.get_by_principal_name(test_admin_principal_name)
client_app = client.applications.get_by_app_id(test_client_id)
# result = resource.get_delegated(client_app, user, app_role).execute_query()
result = resource.get_delegated(test_client_id, user, app_role).execute_query()
if len(result) == 0:
    print("Delegated permission '{0}' is not set".format(app_role))
else:
    print(result.value)
