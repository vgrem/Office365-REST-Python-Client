import os

from examples import acquire_token_by_username_password
from office365.graph_client import GraphClient

client = GraphClient(acquire_token_by_username_password)

# get target folder by path (where 'archive' is a folder path)
folder_item = client.me.drive.root.get_by_path("archive")
chunk_size = 5 * 1024 * 1024


def upload_file(local_path, remove_folder):
    """
    :type local_path: str
    :type remove_folder: office365.onedrive.driveitems.driveItem.DriveItem
    """

    def print_progress(range_pos):
        print("{0} bytes uploaded".format(range_pos))

    remote_file = remove_folder.resumable_upload(local_path, chunk_size=chunk_size,
                                                 chunk_uploaded=print_progress).get().execute_query()
    print(f"File {remote_file.web_url} has been uploaded")


# upload a file
#upload_file("../../tests/data/big_buck_bunny.mp4", folder_item)

dir_name = "../../tests/data"
for file_name in os.listdir(dir_name):
    upload_file(os.path.join(dir_name, file_name), folder_item)
