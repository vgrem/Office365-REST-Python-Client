"""
Create a Text column in a list

https://learn.microsoft.com/en-us/graph/api/list-post-columns?view=graph-rest-1.0
"""

from office365.graph_client import GraphClient
from tests import (
    create_unique_name,
    test_client_id,
    test_password,
    test_tenant,
    test_username,
)

client = GraphClient(tenant=test_tenant).with_username_and_password(
    test_client_id, test_username, test_password
)
lib = client.sites.root.lists["Documents"]
column_name = create_unique_name("TextColumn")
column = lib.columns.add_text(column_name).execute_query()
print(column.display_name)

column.delete_object().execute_query()
