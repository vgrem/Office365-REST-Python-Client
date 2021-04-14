from tests import test_user_principal_name
from tests.graph_case import GraphTestCase


class TestGraphMail(GraphTestCase):

    def test_1_send_mail_json(self):
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
                            "Address": test_user_principal_name
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
        self.client.me.send_mail(message_json).execute_query()

    def test_2_get_my_messages(self):
        messages = self.client.me.messages.top(1).get().execute_query()
        self.assertLessEqual(1, len(messages))
        self.assertIsNotNone(messages[0].resource_path)

    def test_3_update_message(self):
        messages = self.client.me.messages.top(1).get().execute_query()
        message_to_update = messages[0]
        message_to_update.update().execute_query()

    def test_4_delete_message(self):
        messages = self.client.me.messages.top(1).get().execute_query()
        message_to_delete = messages[0]
        message_to_delete.delete_object().execute_query()
