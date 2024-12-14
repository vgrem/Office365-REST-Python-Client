"""
How to grant and revoke delegated permissions for an app using Microsoft Graph.
Delegated permissions, also called scopes or OAuth2 permissions, allow an app to call an API
on behalf of a signed-in user.


https://learn.microsoft.com/en-us/graph/permissions-grant-via-msgraph?tabs=http&pivots=grant-delegated-permissions
"""

from office365.graph_client import GraphClient
from tests import (
    test_client_id,
    test_client_secret,
    test_tenant,
)

client = GraphClient.with_client_secret(test_tenant, test_client_id, test_client_secret)


resource = client.service_principals.get_by_name("Microsoft Graph")
app_role = "ThreatAssessment.Read.All"  # "Bookings.Read.All"
result = resource.get_application_permissions(test_client_id).execute_query()
if (
    len([cur_app_role for cur_app_role in result.value if cur_app_role == app_role])
    == 0
):
    print("Application permission '{0}' is not granted".format(app_role))
else:
    print(result.value)
