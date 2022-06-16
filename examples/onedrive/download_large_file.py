import os
import tempfile

from examples import acquire_token_by_username_password
from office365.graph_client import GraphClient
from office365.onedrive.driveitems.driveItem import DriveItem


def print_download_progress(offset):
    print("Downloaded '{0}' bytes...".format(offset))


client = GraphClient(acquire_token_by_username_password)
# # 1. address file by path and get file metadata
file_item = client.me.drive.root.get_by_path("archive/big_buck_bunny.mp4").get().execute_query()
# 2 download a large file (chunked file download)
with tempfile.TemporaryDirectory() as local_path:
    with open(os.path.join(local_path, file_item.name), 'wb') as local_file:
        file_item.download_session(local_file, print_download_progress).execute_query()
    print("File '{0}' has been downloaded into {1}".format(file_item.name, local_file.name))
