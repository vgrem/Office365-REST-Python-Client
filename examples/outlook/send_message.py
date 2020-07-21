from office365.graph.graph_client import GraphClient
from settings import settings


def get_token(auth_ctx):
    """Acquire token via client credential flow (ADAL Python library is utilized)"""
    token = auth_ctx.acquire_token_with_client_credentials(
        "https://graph.microsoft.com",
        settings['client_credentials']['client_id'],
        settings['client_credentials']['client_secret'])
    return token


client = GraphClient(settings['tenant'], get_token)
message_json = {
    "Message": {
        "Subject": "Meet for lunch?",
        "Body": {
            "ContentType": "Text",
            "Content": "The new cafeteria is open."
        },
        "ToRecipients": [
            {
                "EmailAddress": {
                    "Address": "vgrem@mediadev8.onmicrosoft.com"
                }
            }
        ]
    },
    "SaveToSentItems": "false"
}

login_name = "mdoe@mediadev8.onmicrosoft.com"
client.users[login_name].send_mail(message_json)
client.execute_query()
