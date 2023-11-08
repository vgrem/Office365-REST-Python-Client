"""
Get metadata for a list

https://learn.microsoft.com/en-us/graph/api/list-get?view=graph-rest-1.0
"""

from office365.graph_client import GraphClient
from tests.graph_case import acquire_token_by_client_credentials

client = GraphClient(acquire_token_by_client_credentials)
lib = client.sites.root.lists["Documents"].get().execute_query()
print(lib.web_url)
