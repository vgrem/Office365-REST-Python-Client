"""
Determines whether the delegated permissions is granted by the Microsoft Graph service principal in the tenant.

https://learn.microsoft.com/en-us/graph/permissions-grant-via-msgraph?tabs=http&pivots=grant-delegated-permissions
"""

from office365.graph_client import GraphClient
from tests import (
    test_admin_principal_name,
    test_client_id,
    test_client_secret,
    test_tenant,
)

client = GraphClient.with_client_secret(test_tenant, test_client_id, test_client_secret)

resource = client.service_principals.get_by_name("Microsoft Graph")
scope = "DeviceLocalCredential.Read.All"
user = client.users.get_by_principal_name(test_admin_principal_name)
client_app = client.applications.get_by_app_id(test_client_id)
# result = resource.get_delegated_permissions(test_client_id, user).execute_query()
result = resource.get_delegated_permissions(test_client_id).execute_query()
if len([cur_scope for cur_scope in result.value if cur_scope == scope]) == 0:
    print("Delegated permission '{0}' is not granted".format(scope))
else:
    print(result.value)
