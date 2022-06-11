import os.path
from io import BytesIO
from random import randint

from office365.sharepoint.attachments.attachment import Attachment
from tests.sharepoint.sharepoint_case import SPTestCase

from office365.sharepoint.attachments.creation_information import AttachmentCreationInformation
from office365.sharepoint.listitems.listitem import ListItem
from office365.sharepoint.lists.creation_information import ListCreationInformation
from office365.sharepoint.lists.template_type import ListTemplateType


class TestListItemAttachment(SPTestCase):
    attachment_file_name = "Sample.txt"
    target_item = None  # type: ListItem
    attachment_path = "{0}/../data/{1}".format(os.path.dirname(__file__), attachment_file_name)
    target_attachment = None  # type: Attachment

    @classmethod
    def setUpClass(cls):
        super(TestListItemAttachment, cls).setUpClass()
        list_name = "Tasks" + str(randint(0, 10000))
        target_list = cls.ensure_list(cls.client.web,
                                      ListCreationInformation(list_name,
                                                              None,
                                                              ListTemplateType.Tasks))
        item_properties = {'Title': 'Approval Task'}
        cls.target_item = target_list.add_item(item_properties).execute_query()

    @classmethod
    def tearDownClass(cls):
        cls.target_item.delete_object().execute_query()

    def test1_upload_attachment(self):
        with open(self.attachment_path, 'rb') as content_file:
            file_content = content_file.read()
        attachment_file_information = AttachmentCreationInformation(self.attachment_file_name, file_content)
        attachment = self.__class__.target_item.attachment_files.add(attachment_file_information).execute_query()
        self.assertIsNotNone(attachment.file_name)
        self.__class__.target_attachment = attachment

    def test2_list_attachments(self):
        attachment_files = self.__class__.target_item.attachment_files.get().execute_query()
        self.assertEqual(len(attachment_files), 1)

    def test3_get_by_filename(self):
        attachment_file = self.__class__.target_item.attachment_files.get_by_filename(self.attachment_file_name)
        self.assertIsNotNone(attachment_file.resource_path)

    def test4_download_attachment(self):
        f = BytesIO()
        self.__class__.target_attachment.download(f).execute_query()
        self.assertIsNotNone(f.read())

    def test5_update_attachment(self):
        f_in = BytesIO(b'new attachment content goes here')
        self.__class__.target_attachment.upload(f_in).execute_query()

        f_out = BytesIO()
        self.__class__.target_attachment.download(f_out).execute_query()
        self.assertEqual(f_in.read(), f_out.read())

    def test6_delete_attachments(self):
        self.__class__.target_attachment.delete_object().execute_query()
        attachment_files = self.__class__.target_item.attachment_files.get().execute_query()
        self.assertEqual(len(attachment_files), 0)
