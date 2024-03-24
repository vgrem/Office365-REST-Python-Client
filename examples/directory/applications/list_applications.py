"""
Get the list of applications in this organization
https://learn.microsoft.com/en-us/graph/api/application-list?view=graph-rest-1.0
"""

from office365.graph_client import GraphClient
from tests import test_client_id, test_password, test_tenant, test_username

client = GraphClient.with_username_and_password(
    test_tenant, test_client_id, test_username, test_password
)
apps = client.applications.get().top(10).execute_query()
for app in apps:
    print(app)
