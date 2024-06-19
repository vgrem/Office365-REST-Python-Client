"""
Manage an Azure AD application using Microsoft Graph

https://learn.microsoft.com/en-us/graph/tutorial-applications-basics

You can address an application or a service principal by its ID or by its appId, where ID is referred to
as Object ID and appId is referred to as Application (client) ID on the Azure portal.
"""

from office365.graph_client import GraphClient
from tests import test_client_id, test_client_secret, test_tenant

client = GraphClient.with_client_secret(test_tenant, test_client_id, test_client_secret)
app = client.applications.get_by_app_id(test_client_id).get().execute_query()
print(app)
