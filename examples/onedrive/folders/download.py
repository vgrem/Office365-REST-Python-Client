"""
Download the contents of the driveItem (folder facet)

https://learn.microsoft.com/en-us/graph/api/driveitem-get-content?view=graph-rest-1.0
"""

import os
import tempfile

from office365.graph_client import GraphClient
from office365.onedrive.driveitems.driveItem import DriveItem
from tests import test_client_id, test_password, test_tenant, test_username


def print_progress(downloaded_file):
    # type: (DriveItem) -> None
    print("File {0} has been downloaded..".format(downloaded_file.web_url))


client = GraphClient(tenant=test_tenant).with_username_and_password(
    test_client_id, test_username, test_password
)
folder_item = client.me.drive.root.get_by_path("archive")

zip_path = os.path.join(tempfile.mkdtemp(), "download.zip")
with open(zip_path, "wb") as f:
    folder_item.download_folder(f, print_progress).execute_query()
print("Folder has been downloaded to {0}".format(zip_path))
