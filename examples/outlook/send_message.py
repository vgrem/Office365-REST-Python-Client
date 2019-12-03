from office365.outlookservices.outlook_client import OutlookClient
from office365.runtime.auth.authentication_context import AuthenticationContext
from settings import settings

ctx_auth = AuthenticationContext(url=settings['tenant'])
ctx_auth.acquire_token_password_grant(client_credentials=settings['client_credentials'],
                                      user_credentials=settings['user_credentials'])
client = OutlookClient(ctx_auth)

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
                    "Address": "jdoe@mediadev8.onmicrosoft.com"
                }
            }
        ],
        "Attachments": [
            {
                "@odata.type": "#Microsoft.OutlookServices.FileAttachment",
                "Name": "menu.txt",
                "ContentBytes": "bWFjIGFuZCBjaGVlc2UgdG9kYXk="
            }
        ]
    },
    "SaveToSentItems": "false"
}

client.me.sendmail(message_payload)
client.execute_query()
