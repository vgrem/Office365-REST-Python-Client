from tests.graph.graph_case import GraphTestCase


class TestGraphMail(GraphTestCase):

    def test1_send_mail_json(self):
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
        self.client.me.send_mail(message_json)
        self.client.execute_query()

