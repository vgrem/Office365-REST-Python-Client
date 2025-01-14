"""
Retrieves site columns

https://learn.microsoft.com/en-us/graph/api/site-list-columns?view=graph-rest-1.0
"""

from office365.graph_client import GraphClient
from tests import test_client_id, test_password, test_tenant, test_username

client = GraphClient(tenant=test_tenant).with_username_and_password(
    test_client_id, test_username, test_password
)
columns = client.sites.root.columns.get().execute_query()
for column in columns:
    print(column)
