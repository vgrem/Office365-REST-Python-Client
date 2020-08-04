import os.path
from io import BytesIO
from random import randint

from tests.sharepoint.sharepoint_case import SPTestCase

from office365.sharepoint.attachments.attachmentfile_creation_information import AttachmentfileCreationInformation
from office365.sharepoint.listitems.listitem import ListItem
from office365.sharepoint.lists.list_creation_information import ListCreationInformation
from office365.sharepoint.lists.list_template_type import ListTemplateType


class TestListItemAttachment(SPTestCase):
    attachment_file_name = "SharePoint User Guide.docx"
    target_item = None  # type: ListItem
    attachment_path = "{0}/../data/{1}".format(os.path.dirname(__file__), attachment_file_name)

    @classmethod
    def setUpClass(cls):
        super(TestListItemAttachment, cls).setUpClass()
        list_name = "Tasks" + str(randint(0, 10000))
        cls.target_list = cls.ensure_list(cls.client.web,
                                          ListCreationInformation(list_name,
                                                                  None,
                                                                  ListTemplateType.Tasks))
        item_properties = {'Title': 'Approval Task'}
        cls.target_item = cls.target_list.add_item(item_properties)
        cls.client.execute_query()

    @classmethod
    def tearDownClass(cls):
        cls.target_item.delete_object()
        cls.client.execute_query()

    def test1_upload_attachment(self):
        with open(self.attachment_path, 'rb') as content_file:
            file_content = content_file.read()
        attachment_file_information = AttachmentfileCreationInformation(self.attachment_file_name, file_content)
        created_file = self.__class__.target_item.attachmentFiles.add(attachment_file_information)
        self.client.execute_query()
        self.assertIsNotNone(created_file.properties["FileName"])

    def test2_load_attachments(self):
        attachment_files = self.__class__.target_item.attachmentFiles
        self.client.load(attachment_files)
        self.client.execute_query()
        self.assertEqual(len(attachment_files), 1)
        self.assertEqual(attachment_files[0].properties['FileName'], self.attachment_file_name)

    def test3_download_attachments(self):
        attachment_file = self.__class__.target_item.attachmentFiles.get_by_filename(self.attachment_file_name)
        f = BytesIO()
        attachment_file.download(f)
        self.client.execute_query()
        self.assertIsNotNone(f.read())

    def test4_update_attachments(self):
        attachment_file = self.__class__.target_item.attachmentFiles.get_by_filename(self.attachment_file_name)
        f_in = BytesIO(b'new attachment content goes here')
        attachment_file.upload(f_in)
        self.client.execute_query()

        f_out = BytesIO()
        attachment_file.download(f_out)
        self.client.execute_query()
        self.assertEqual(f_in.read(), f_out.read())

    def test5_delete_attachments(self):
        attachment_file = self.__class__.target_item.attachmentFiles.get_by_filename(self.attachment_file_name)
        attachment_file.delete_object()
        attachment_files = self.__class__.target_item.attachmentFiles
        self.client.load(attachment_files)
        self.client.execute_query()
        self.assertEqual(len(attachment_files), 0)
