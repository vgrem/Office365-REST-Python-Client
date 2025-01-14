"""
Demonstrates how to upload files from a local folder into OneDrive drive
"""

from office365.graph_client import GraphClient
from office365.onedrive.driveitems.driveItem import DriveItem
from tests import test_client_id, test_password, test_tenant, test_username


def print_progress(uploaded_file):
    # type: (DriveItem)-> None
    print("File has been uploaded into '{0}'".format(uploaded_file.web_url))


client = GraphClient(tenant=test_tenant).with_username_and_password(
    test_client_id, test_username, test_password
)
local_path = "../../data"
drive_item = client.me.drive.root.get_by_path("Import")
drive_item.upload_folder(local_path, print_progress).execute_query()
