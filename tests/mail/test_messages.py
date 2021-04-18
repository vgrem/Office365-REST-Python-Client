from office365.mail.message import Message
from tests import test_user_principal_name, test_user_principal_name_alt
from tests.graph_case import GraphTestCase


class TestGraphMail(GraphTestCase):
    target_message = None  # type: Message

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

    def test2_create_draft_message(self):
        draft_message = self.client.me.messages.add("Meet for lunch?",
                                                    "The new cafeteria is open.",
                                                    [test_user_principal_name]).execute_query()
        self.assertIsNotNone(draft_message.id)
        self.__class__.target_message = draft_message

    def test3_send_message(self):
        self.__class__.target_message.send().execute_query()

    #def test4_forward_message(self):
    #    self.__class__.target_message.forward([test_user_principal_name_alt]).execute_query()

    def test_5_get_my_messages(self):
        messages = self.client.me.messages.top(1).get().execute_query()
        self.assertLessEqual(1, len(messages))
        self.assertIsNotNone(messages[0].resource_path)

    def test_6_update_message(self):
        messages = self.client.me.messages.top(1).get().execute_query()
        message_to_update = messages[0]
        message_to_update.update().execute_query()

    def test_7_delete_message(self):
        messages = self.client.me.messages.top(1).get().execute_query()
        message_to_delete = messages[0]
        message_to_delete.delete_object().execute_query()
