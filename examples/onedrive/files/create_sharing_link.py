"""
Create a sharing link for a DriveItem

The following example requests a sharing link to be created for the DriveItem in the user's OneDrive.
The sharing link is configured to be read-only and usable by anyone with the link.
All existing permissions are removed when sharing for the first time if retainInheritedPermissions is false.

https://learn.microsoft.com/en-us/graph/api/driveitem-createlink?view=graph-rest-1.0
"""

from office365.graph_client import GraphClient
from tests import test_client_id, test_password, test_tenant, test_username

client = GraphClient(tenant=test_tenant).with_username_and_password(
    test_client_id, test_username, test_password
)
file_path = "Financial Sample.xlsx"
drive_item = client.me.drive.root.get_by_path(file_path)
permission = drive_item.create_link(
    "view", "anonymous", password="ThisIsMyPrivatePassword"
).execute_query()
print(permission.link)
