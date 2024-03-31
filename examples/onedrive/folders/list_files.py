"""
Gets folders from drive
https://learn.microsoft.com/en-us/graph/api/driveitem-list-children?view=graph-rest-1.0
"""
from office365.graph_client import GraphClient
from tests import test_client_id, test_password, test_tenant, test_username
from tests.graph_case import acquire_token_by_username_password

client = GraphClient.with_username_and_password(
    test_tenant, test_client_id, test_username, test_password
)
items = client.me.drive.root.get_files(False).execute_query()
# items = client.sites.root.lists["Documents"].drive.root.get_files(True).execute_query()
for file_item in items:
    print(file_item.web_url)
