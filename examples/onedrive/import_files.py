import os
from os.path import isfile, join

import adal
from settings import settings

from office365.graph_client import GraphClient


def get_token():
    """Acquire token via client credential flow
    """
    authority_url = 'https://login.microsoftonline.com/{0}'.format(settings['tenant'])
    auth_ctx = adal.AuthenticationContext(authority_url)
    token = auth_ctx.acquire_token_with_client_credentials(
        "https://graph.microsoft.com",
        settings['client_credentials']['client_id'],
        settings['client_credentials']['client_secret'])
    return token


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


# get target drive
client = GraphClient(get_token)
user_name = settings.get('test_alt_account_name')
target_drive = client.users[user_name].drive
# import local files into OneDrive
upload_files(target_drive, "../data")
