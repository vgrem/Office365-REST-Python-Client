import adal

from settings import settings

from office365.graph_client import GraphClient


def get_token():
    """Acquire token via client credential flow (ADAL Python library is utilized)"""
    authority_url = 'https://login.microsoftonline.com/{0}'.format(settings['tenant'])
    auth_ctx = adal.AuthenticationContext(authority_url)
    token = auth_ctx.acquire_token_with_client_credentials(
        "https://graph.microsoft.com",
        settings['client_credentials']['client_id'],
        settings['client_credentials']['client_secret'])
    return token


client = GraphClient(get_token)
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
