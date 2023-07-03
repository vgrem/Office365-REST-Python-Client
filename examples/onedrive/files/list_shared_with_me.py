"""
Retrieves a collection of DriveItem resources that have been shared with the current user
"""
from office365.graph_client import GraphClient
from office365.onedrive.driveitems.driveItem import DriveItem
from tests.graph_case import acquire_token_by_username_password


client = GraphClient(acquire_token_by_username_password)
drive_items = client.me.drive.shared_with_me().execute_query()
for item in drive_items:  # type: DriveItem
    print("Drive Item url: {0}".format(item.web_url))
