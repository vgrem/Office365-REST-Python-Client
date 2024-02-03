"""
Retrieve the metadata for a driveItem in a drive by file system path

https://learn.microsoft.com/en-us/graph/api/driveitem-get?view=graph-rest-1.0
"""

from office365.graph_client import GraphClient
from tests import test_client_id, test_password, test_tenant, test_username

client = GraphClient.with_username_and_password(
    test_tenant, test_client_id, test_username, test_password
)
file_path = "Financial Sample.xlsx"
file_item = client.me.drive.root.get_by_path(file_path).get().execute_query()
print(file_item.web_url)
