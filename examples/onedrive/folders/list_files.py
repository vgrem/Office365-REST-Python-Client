"""
Gets folders from drive
https://learn.microsoft.com/en-us/graph/api/driveitem-list-children?view=graph-rest-1.0
"""
from office365.graph_client import GraphClient
from tests.graph_case import acquire_token_by_username_password

client = GraphClient(acquire_token_by_username_password)
drive = client.me.drive
file_items = client.me.drive.root.get_files(True).execute_query()
for file_item in file_items:
    print(file_item.web_url)
