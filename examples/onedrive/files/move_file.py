"""
This example moves an item specified by {server relative path} into a folder specified by
server relative path.

https://learn.microsoft.com/en-us/graph/api/driveitem-move?view=graph-rest-1.0
"""

from office365.graph_client import GraphClient
from office365.onedrive.driveitems.conflict_behavior import ConflictBehavior
from tests import test_client_id, test_password, test_tenant, test_username

client = GraphClient.with_username_and_password(
    test_tenant, test_client_id, test_username, test_password
)

local_path = "../../data/Financial Sample.xlsx"
source_file = client.me.drive.root.upload_file(local_path).execute_query()
target_path = "archive/2018"
target_folder = client.me.drive.root.get_by_path(target_path)
target_file = source_file.move(
    parent=target_folder, conflict_behavior=ConflictBehavior.Replace
).execute_query()
print(target_file.web_url)
