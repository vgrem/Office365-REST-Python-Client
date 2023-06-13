"""
Retrieve the metadata for a driveItem in a drive by file system path

https://learn.microsoft.com/en-us/graph/api/driveitem-get?view=graph-rest-1.0&tabs=http
"""

from office365.graph_client import GraphClient
from tests.graph_case import acquire_token_by_username_password

client = GraphClient(acquire_token_by_username_password)
file_path = "archive/Sample.rtf"
file_item = client.me.drive.root.get_by_path(file_path).get().execute_query()
print(file_item.web_url)
