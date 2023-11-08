"""
Retrieves site columns

https://learn.microsoft.com/en-us/graph/api/site-list-columns?view=graph-rest-1.0
"""
from office365.graph_client import GraphClient
from tests.graph_case import acquire_token_by_username_password

client = GraphClient(acquire_token_by_username_password)
columns = client.sites.root.columns.get().execute_query()
for column in columns:
    print(column)
