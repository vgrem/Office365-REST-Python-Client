from office365.graphClient import GraphClient
from settings import settings


def get_token(auth_ctx):
    """Acquire token via client credential flow (ADAL Python library is utilized)"""
    token = auth_ctx.acquire_token_with_client_credentials(
        "https://graph.microsoft.com",
        settings['client_credentials']['client_id'],
        settings['client_credentials']['client_secret'])
    return token


client = GraphClient(settings['tenant'], get_token)
my_drive = client.users["jdoe@mediadev8.onmicrosoft.com"].drive
client.load(my_drive)
client.execute_query()
print("OK")
