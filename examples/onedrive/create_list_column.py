from examples import acquire_token_by_username_password
from office365.graph_client import GraphClient
from office365.onedrive.lists.list import List

client = GraphClient(acquire_token_by_username_password)
lib = client.sites.root.lists["Documents"]  # type: List
column = lib.columns.add_text("CustomName2").execute_query()
print(column.display_name)
