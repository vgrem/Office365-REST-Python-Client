import os
import tempfile
from office365.graph.graph_client import GraphClient
from settings import settings


def get_token(auth_ctx):
    """Acquire token via client credential flow (ADAL Python library is utilized)
    :type auth_ctx: adal.AuthenticationContext
    """
    token = auth_ctx.acquire_token_with_client_credentials(
        "https://graph.microsoft.com",
        settings['client_credentials']['client_id'],
        settings['client_credentials']['client_secret'])
    return token


def download_files(remote_folder, local_path):
    drive_items = remote_folder.children
    client.load(drive_items)
    client.execute_query()
    for drive_item in drive_items:
        if not drive_item.file.is_server_object_null:  # is file?
            # download file content
            with open(os.path.join(local_path, drive_item.name), 'wb') as local_file:
                drive_item.download(local_file)
                client.execute_query()
            print("File '{0}' has been downloaded".format(local_file.name))


# example demonstrates how to export OneDrive files into local file system

# connect
client = GraphClient(settings['tenant'], get_token)

# load drive properties
drive = client.users["jdoe@mediadev8.onmicrosoft.com"].drive
client.load(drive)
client.execute_query()

# download files from OneDrive
with tempfile.TemporaryDirectory() as path:
    download_files(drive.root, path)
    print("Done")

