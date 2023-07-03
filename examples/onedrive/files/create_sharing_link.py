"""
Create a sharing link for a DriveItem

The following example requests a sharing link to be created for the DriveItem in the user's OneDrive.
The sharing link is configured to be read-only and usable by anyone with the link.
All existing permissions are removed when sharing for the first time if retainInheritedPermissions is false.

https://learn.microsoft.com/en-us/graph/api/driveitem-createlink?view=graph-rest-1.0&tabs=http
"""
from office365.graph_client import GraphClient
from tests.graph_case import acquire_token_by_username_password


client = GraphClient(acquire_token_by_username_password)
file_path = "archive/Sample.rtf"
drive_item = client.me.drive.root.get_by_path(file_path)
permission = drive_item.create_link("view", "anonymous", password="ThisIsMyPrivatePassword").execute_query()
print(permission.link)
