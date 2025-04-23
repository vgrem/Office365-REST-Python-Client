"""
List sharing permissions on a driveItem

https://learn.microsoft.com/en-us/graph/api/driveitem-list-permissions?view=graph-rest-1.0
"""

from office365.graph_client import GraphClient
from tests import test_client_id, test_password, test_tenant, test_username

client = GraphClient(tenant=test_tenant).with_username_and_password(
    test_client_id, test_username, test_password
)
file_path = "Archive/Financial Sample.xlsx"
file_item = client.me.drive.root.get_by_path(file_path)
permissions = file_item.permissions.get().execute_query()
for perm in permissions:
   print(perm.granted_to_v2)
