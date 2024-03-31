"""
Demonstrates how to create a new OneNote notebook

https://learn.microsoft.com/en-us/graph/api/onenote-post-notebooks?view=graph-rest-1.0
"""

from office365.graph_client import GraphClient
from tests import (
    create_unique_name,
    test_client_id,
    test_password,
    test_tenant,
    test_username,
)

client = GraphClient.with_username_and_password(
    test_tenant, test_client_id, test_username, test_password
)
display_name = create_unique_name("My Private notebook")
notebook = client.me.onenote.notebooks.add(display_name).execute_query()
print(notebook.display_name)
