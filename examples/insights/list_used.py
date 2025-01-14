"""
Calculate and list the documents that a user has viewed or modified.

https://learn.microsoft.com/en-us/graph/api/insights-list-used?view=graph-rest-1.0
"""

from office365.graph_client import GraphClient
from tests import test_client_id, test_password, test_tenant, test_username

client = GraphClient(tenant=test_tenant).with_username_and_password(
    test_client_id, test_username, test_password
)
result = client.me.insights.used.get().execute_query()
for item in result:
    print("Resource: {0}".format(item.resource_reference))
