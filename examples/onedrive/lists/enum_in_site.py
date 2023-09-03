"""
Enumerate lists in a site

https://learn.microsoft.com/en-us/graph/api/list-list?view=graph-rest-1.0
"""

from office365.graph_client import GraphClient
from office365.onedrive.lists.list import List
from tests.graph_case import acquire_token_by_client_credentials

client = GraphClient(acquire_token_by_client_credentials)
lists = client.sites.root.lists.get().execute_query()
for lst in lists:  # type: List
    print(lst.display_name)
