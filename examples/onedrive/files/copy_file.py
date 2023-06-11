"""
This example copies a file identified by {server relative path} into a folder identified with a {server relative path}.
The new copy of the file will be named Sample (copy).rtf.

https://learn.microsoft.com/en-us/graph/api/driveitem-copy?view=graph-rest-1.0&tabs=http
"""
from office365.graph_client import GraphClient
from tests.graph_case import acquire_token_by_username_password

client = GraphClient(acquire_token_by_username_password)
source_path = "archive/Sample.rtf"
new_name = "Sample (copy).rtf"
target_path = "archive/2018"
source_file_item = client.me.drive.root.get_by_path(source_path)  # source file item
target_folder_item = client.me.drive.root.get_by_path(target_path)  # target folder item
# result = source_file_item.copy(name=new_name).execute_query()  # copy to the same folder with a different name
result = source_file_item.copy(parent=target_folder_item).execute_query()  # copy to another folder
print(result.value)
