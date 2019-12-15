from unittest import TestCase

from office365.graphClient import GraphClient
from settings import settings


def get_token(auth_ctx):
    token = auth_ctx.acquire_token_with_username_password(
        'https://graph.microsoft.com',
        settings['user_credentials']['username'],
        settings['user_credentials']['password'],
        settings['client_credentials']['client_id'])
    return token


class TestGraphMail(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.client = GraphClient(settings['tenant'], get_token)

    def test1_send_mail(self):
        message = {
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
        self.client.me.send_mail(message)
        self.client.execute_query()
