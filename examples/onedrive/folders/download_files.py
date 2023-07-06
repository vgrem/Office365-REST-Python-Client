import os
import tempfile

from office365.graph_client import GraphClient
from office365.onedrive.driveitems.driveItem import DriveItem
from tests.graph_case import acquire_token_by_username_password

client = GraphClient(acquire_token_by_username_password)
# address folder by path
folder_item = client.me.drive.root.get_by_path("archive").get().execute_query()

with tempfile.TemporaryDirectory() as local_path:
    items = folder_item.children.get().execute_query()
    for drive_item in items:  # type: DriveItem
        if drive_item.is_file:
            with open(os.path.join(local_path, drive_item.name), 'wb') as local_file:
                drive_item.download(local_file).execute_query()  # download file content
            print("File '{0}' has been downloaded into {1}".format(drive_item.name, local_file.name))
