"""
This example moves an item specified by {server relative path} into a folder specified by
server relative path.

https://learn.microsoft.com/en-us/graph/api/driveitem-move?view=graph-rest-1.0
"""
from office365.graph_client import GraphClient
from tests.graph_case import acquire_token_by_username_password

client = GraphClient(acquire_token_by_username_password)
source_path = "archive/Sample.rtf"
target_path = "archive/2018"
source_file_item = client.me.drive.root.get_by_path(source_path)
target_folder_item = client.me.drive.root.get_by_path(target_path)
result = source_file_item.move(parent=target_folder_item).execute_query()
print(result.value)
