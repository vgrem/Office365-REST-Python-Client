"""
Calculated insight that includes the list of documents shared with a user.

This insight includes documents hosted on OneDrive/SharePoint in the user's Microsoft 365 tenant that are shared with
the user, and documents that are attached as files and sent to the user.

https://learn.microsoft.com/en-us/graph/api/insights-list-shared?view=graph-rest-1.0
"""

from office365.graph_client import GraphClient
from tests import test_client_id, test_password, test_tenant, test_username

client = GraphClient(tenant=test_tenant).with_username_and_password(
    test_client_id, test_username, test_password
)
result = client.me.insights.shared.get().execute_query()
for item in result:
    print("Resource url: {0}".format(item.resource_reference))
