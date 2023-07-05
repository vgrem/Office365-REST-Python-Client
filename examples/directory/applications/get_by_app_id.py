"""
Manage an Azure AD application using Microsoft Graph

https://learn.microsoft.com/en-us/graph/tutorial-applications-basics?tabs=http

You can address an application or a service principal by its ID or by its appId, where ID is referred to
as Object ID and appId is refered to as Application (client) ID on the Azure portal.
"""
from office365.graph_client import GraphClient
from tests import test_client_credentials
from tests.graph_case import acquire_token_by_client_credentials

client = GraphClient(acquire_token_by_client_credentials)
app = client.applications.get_by_app_id(test_client_credentials.clientId).get().execute_query()
print(app.display_name)
