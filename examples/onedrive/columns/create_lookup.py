"""
Creates a lookup column in a list

https://learn.microsoft.com/en-us/graph/api/list-post-columns?view=graph-rest-1.0
"""

from office365.graph_client import GraphClient
from tests import create_unique_name
from tests.graph_case import acquire_token_by_username_password

client = GraphClient(acquire_token_by_username_password)
lib = client.sites.root.lists["Documents"]

column_name = create_unique_name("LookupColumn")
lookup_column = lib.columns.add_lookup(column_name, lib).execute_query()
print(lookup_column.display_name)

lookup_column.delete_object().execute_query()  # clean up
