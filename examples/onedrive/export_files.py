import os
from os.path import isfile, join
from settings import settings

from office365.graphClient import GraphClient

export_settings = {
    "sourcePath": "../data",
    "targetDrive": {

    }
}


def get_token(auth_ctx):
    """Acquire token via client credential flow (ADAL Python library is utilized)"""
    token = auth_ctx.acquire_token_with_client_credentials(
        "https://graph.microsoft.com",
        settings['client_credentials']['client_id'],
        settings['client_credentials']['client_secret'])
    return token


def get_file_names():
    return [f for f in os.listdir(export_settings['sourcePath']) if
            isfile(join(export_settings['sourcePath'], f))]


def get_file_content(name):
    path = os.path.join(export_settings['sourcePath'], file_name)
    with open(path, 'rb') as content_file:
        return content_file.read()


client = GraphClient(settings['tenant'], get_token)
result = client.drives.top(1)
client.load(result)
client.execute_query()
if len(result) != 1:
    print("No drive was found")
    exit()

target_drive = result[0]
for file_name in get_file_names():
    print("Reading local file: {0}".format(file_name))
    file_content = get_file_content(file_name)
    uploaded_file = target_drive.root.upload(file_name, file_content)
    client.execute_query()
    print("File has been uploaded into: {0}".format(uploaded_file.webUrl))
