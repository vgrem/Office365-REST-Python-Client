"""
Create a new list

The following is an example of how to create a new generic list

https://learn.microsoft.com/en-us/graph/api/list-create?view=graph-rest-1.0
"""
from office365.graph_client import GraphClient
from tests import create_unique_name
from tests.graph_case import acquire_token_by_client_credentials

client = GraphClient(acquire_token_by_client_credentials)

print("Creating a custom list...")
custom_list = client.sites.root.lists.add(
    create_unique_name("Books"), "genericList"
).execute_query()
print("List has been created at {0}".format(custom_list.web_url))

print("Cleaning up resources...")
custom_list.delete_object().execute_query()
