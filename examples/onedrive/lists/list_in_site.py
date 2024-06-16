"""
Enumerate lists in a site

https://learn.microsoft.com/en-us/graph/api/list-list?view=graph-rest-1.0
"""

from office365.graph_client import GraphClient
from tests import test_client_id, test_client_secret, test_tenant

client = GraphClient.with_client_secret(test_tenant, test_client_id, test_client_secret)
lists = client.sites.root.lists.get().execute_query()
for lst in lists:
    print(lst.display_name)
