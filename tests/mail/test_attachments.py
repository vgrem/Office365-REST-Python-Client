from office365.mail.attachment_item import AttachmentItem
from office365.mail.attachment_type import AttachmentType
from office365.mail.message import Message
from tests import test_user_principal_name
from tests.graph_case import GraphTestCase


class TestAttachments(GraphTestCase):
    target_message = None  # type: Message

    @classmethod
    def setUpClass(cls):
        super(TestAttachments, cls).setUpClass()
        cls.target_message = cls.client.me.messages.add("Meet for lunch?",
                                                        "The new cafeteria is open.",
                                                        [test_user_principal_name]).execute_query()

    @classmethod
    def tearDownClass(cls):
        cls.target_message.delete_object().execute_query()

    def test1_create_upload_session(self):
        message_id = self.__class__.target_message.id
        attachment_item = AttachmentItem(attachmentType=AttachmentType.file, name="flower", size=3483322)
        result = self.client.me.messages[message_id].attachments.create_upload_session(attachment_item).execute_query()
        self.assertIsNotNone(result.value)
