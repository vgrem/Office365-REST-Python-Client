from office365.mail.mailFolder import MailFolder
from tests.graph_case import GraphTestCase


class TestGraphMail(GraphTestCase):
    target_mail_folder = None  # type: MailFolder

    def test1_list_mail_folder(self):
        available_mail_folders = self.client.me.mail_folders.get().execute_query()
        self.assertIsNotNone(available_mail_folders.resource_path)
        # self.__class__.target_message = draft_message


