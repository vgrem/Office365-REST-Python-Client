from tests.graph_case import GraphTestCase


class TestGraphMail(GraphTestCase):

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
