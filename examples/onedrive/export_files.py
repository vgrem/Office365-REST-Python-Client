import os
from os.path import isfile, join

from office365.graph_client import GraphClient

tenant_name = "mediadev8.onmicrosoft.com"
client_id, client_secret = os.environ['Office365_Python_Sdk_ClientCredentials'].split(';')
login_name, password = os.environ['Office365_Python_Sdk_Credentials'].split(';')


def get_token(auth_ctx):
    """Acquire token via client credential flow (ADAL Python library is utilized)"""
    token = auth_ctx.acquire_token_with_client_credentials(
        "https://graph.microsoft.com",
        client_id,
        client_secret)
    return token


settings = {
    "sourcePath": "../data",
    "targetDrive": {

    }
}

client = GraphClient(tenant_name, get_token)
target_drive = client.users[login_name].drive
client.load(target_drive)
client.execute_query()

file_names = [f for f in os.listdir(settings['sourcePath']) if isfile(join(settings['sourcePath'], f))]
for file_name in file_names:
    file_path = os.path.join(settings['sourcePath'], file_name)
    print("Reading local file: {0}".format(file_name))
    with open(file_path, 'rb') as content_file:
        file_content = content_file.read()
    print("Uploading file into: {0}".format(target_drive.web_url))
    target_drive.root.upload_file(file_name, file_content)
    client.execute_query()



