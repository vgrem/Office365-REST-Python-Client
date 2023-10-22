"""
List groups

https://learn.microsoft.com/en-us/graph/api/user-list?view=graph-rest-1.0
"""

from office365.graph_client import GraphClient
from tests.graph_case import acquire_token_by_username_password

client = GraphClient(acquire_token_by_username_password)
groups = client.groups.get().top(10).execute_query()
for grp in groups:
    print(grp.display_name)
