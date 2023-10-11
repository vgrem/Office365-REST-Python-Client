"""
Create a Text column in a list

https://learn.microsoft.com/en-us/graph/api/list-post-columns?view=graph-rest-1.0
"""

from office365.graph_client import GraphClient
from tests import create_unique_name
from tests.graph_case import acquire_token_by_username_password

client = GraphClient(acquire_token_by_username_password)
lib = client.sites.root.lists["Docs"]
column_name = create_unique_name("TextColumn")
column = lib.columns.add_text(column_name).execute_query()
print(column.display_name)

column.delete_object().execute_query()
