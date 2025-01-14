"""
Get metadata for a list

https://learn.microsoft.com/en-us/graph/api/list-get?view=graph-rest-1.0
"""

from office365.graph_client import GraphClient
from tests import test_client_id, test_client_secret, test_tenant

client = GraphClient(tenant=test_tenant).with_client_secret(
    test_client_id, test_client_secret
)
# lib = client.sites.root.lists["Documents"].get().execute_query()
lib = client.sites.root.lists.get_by_name("Documents").get().execute_query()
print(lib.web_url)
