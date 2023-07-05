"""
Demonstrates how to create a new OneNote notebook

https://learn.microsoft.com/en-us/graph/api/onenote-post-notebooks?view=graph-rest-1.0&tabs=http
"""

from office365.graph_client import GraphClient
from tests import create_unique_name
from tests.graph_case import acquire_token_by_username_password

client = GraphClient(acquire_token_by_username_password)
display_name = create_unique_name("My Private notebook")
notebook = client.me.onenote.notebooks.add(display_name).execute_query()
print(notebook.display_name)

