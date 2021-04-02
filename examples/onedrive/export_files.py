import os
import tempfile

from examples import acquire_token_client_credentials
from office365.graph_client import GraphClient


def download_files(remote_folder, local_path):
    """

    :type remote_folder: office365.onedrive.driveItem.DriveItem
    :type local_path: str
    """
    drive_items = remote_folder.children.get().execute_query()
    for drive_item in drive_items:
        if not drive_item.file.is_server_object_null:  # is file?
            # download file content
            with open(os.path.join(local_path, drive_item.name), 'wb') as local_file:
                drive_item.download(local_file)
                client.execute_query()
            print("File '{0}' has been downloaded".format(local_file.name))


# --------------------------------------------------------------------------
# Example demonstrates how to export OneDrive files into local file system
# --------------------------------------------------------------------------

# connect
client = GraphClient(acquire_token_client_credentials)

# load drive properties
target_user_name = settings.get('first_account_name')
drive = client.users[target_user_name].drive
# download files from OneDrive
with tempfile.TemporaryDirectory() as path:
    download_files(drive.root, path)
    print("Done")
