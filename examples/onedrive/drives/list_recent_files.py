"""
List recent files

https://learn.microsoft.com/en-us/graph/api/drive-recent?view=graph-rest-1.0
"""

from office365.graph_client import GraphClient
from tests import test_client_id, test_password, test_tenant, test_username

client = GraphClient(tenant=test_tenant).with_username_and_password(
    test_client_id, test_username, test_password
)
items = client.me.drive.recent().execute_query()
for item in items:
    print(item.web_url)
