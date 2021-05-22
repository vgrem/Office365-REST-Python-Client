import os
from os.path import isfile, join

from examples import acquire_token_by_client_credentials
from office365.graph_client import GraphClient
from tests import load_settings


def upload_files(remote_drive, local_root_path):
    """
    Uploads files from local folder into OneDrive drive

    :type remote_drive: Drive
    :type local_root_path: str
    """
    for name in os.listdir(local_root_path):
        path = join(local_root_path, name)
        if isfile(path):
            with open(path, 'rb') as local_file:
                content = local_file.read()
            uploaded_drive_item = remote_drive.root.upload(name, content).execute_query()
            print("File '{0}' uploaded into {1}".format(path, uploaded_drive_item.web_url), )


settings = load_settings()
client = GraphClient(acquire_token_by_client_credentials)
test_user_principal_name_alt = settings.get('users', 'test_user2')
target_drive = client.users[test_user_principal_name_alt].drive  # get target drive
# import local files into OneDrive
upload_files(target_drive, "../data")
