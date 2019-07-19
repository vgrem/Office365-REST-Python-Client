import os

from office365.graph_client import GraphClient


def get_token(auth_ctx):
    token = auth_ctx.acquire_token_with_client_credentials(
        "https://graph.microsoft.com",
        client_id,
        client_secret)
    return token


tenant_name = "mediadev88.onmicrosoft.com"
client_id, client_secret = os.environ['Office365_Python_Sdk_ClientCredentials'].split(';')

client = GraphClient(tenant_name, get_token)
drives = client.drives
client.load(drives)
client.execute_query()
for drive in drives:
    print("Drive url: {0}".format(drive.web_url))
