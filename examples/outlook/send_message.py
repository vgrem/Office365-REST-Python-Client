import os
from office365.graphClient import GraphClient


def get_token(auth_ctx):
    token = auth_ctx.acquire_token_with_client_credentials(
        "https://graph.microsoft.com",
        client_id,
        client_secret)
    return token


tenant_name = "mediadev8.onmicrosoft.com"
client_id, client_secret = os.environ['Office365_Python_Sdk_ClientCredentials'].split(';')
client = GraphClient(tenant_name, get_token)

message_payload = {
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
client.users[login_name].send_mail(message_payload)
client.execute_query()
