import os.path

from office365.sharepoint.attachmentfile_creation_information import AttachmentfileCreationInformation
from office365.sharepoint.list_creation_information import ListCreationInformation
from office365.sharepoint.list_template_type import ListTemplateType
from tests.sharepoint_case import SPTestCase
from tests.test_utilities import ListExtensions, read_file_as_binary


class TestListItemAttachment(SPTestCase):
    attachment_file_name = "SharePoint User Guide.docx"

    @classmethod
    def setUpClass(cls):
        super(TestListItemAttachment, cls).setUpClass()
        cls.target_list = ListExtensions.ensure_list(cls.context.web,
                                                     ListCreationInformation("Tasks",
                                                                             None,
                                                                             ListTemplateType.Tasks))
        item_properties = {'Title': 'Approval Task'}
        cls.target_item = cls.target_list.add_item(item_properties)
        cls.context.execute_query()

    @classmethod
    def tearDownClass(cls):
        cls.target_item.delete_object()
        cls.context.execute_query()

    def test_1_add_attachment(self):
        file_content = self.read_attachment_file()
        attachment_file_information = AttachmentfileCreationInformation(self.attachment_file_name, file_content)

        created_file = self.target_item.attachment_files.add(attachment_file_information)
        self.context.execute_query()
        self.assertIsNotNone(created_file.properties["FileName"])

    def test_2_list_attachments(self):
        attachment_files = self.target_item.attachment_files
        self.context.load(attachment_files)
        self.context.execute_query()

        attachment_files_items = list(attachment_files)
        self.assertEqual(len(attachment_files_items), 1)
        self.assertEqual(attachment_files_items[0].properties['FileName'], self.attachment_file_name)

    def test_3_read_attachments(self):
        attachment_file = self.target_item.attachment_files.get_by_filename(self.attachment_file_name)
        self.context.load(attachment_file)
        self.context.execute_query()
        data = attachment_file.read()

        file_content = self.read_attachment_file()
        self.assertEqual(data, file_content)

    def test_4_update_attachments(self):
        attachment_file = self.target_item.attachment_files.get_by_filename(self.attachment_file_name)
        self.context.load(attachment_file)
        self.context.execute_query()

        updated_data = os.urandom(1024)
        attachment_file.write(updated_data)

        self.context.load(attachment_file)
        self.context.execute_query()

        data = attachment_file.read()

        self.assertEqual(data, updated_data)

    def test_5_delete_attachments(self):
        attachment_file = self.target_item.attachment_files.get_by_filename(self.attachment_file_name)
        self.context.load(attachment_file)
        self.context.execute_query()

        attachment_file.delete_object()
        self.context.execute_query()

        attachment_files = self.target_item.attachment_files
        self.context.load(attachment_files)
        self.context.execute_query()
        attachment_files_items = list(attachment_files)

        self.assertEqual(len(attachment_files_items), 0)

    def read_attachment_file(self):
        path = "{0}/data/{1}".format(os.path.dirname(__file__), self.attachment_file_name)
        return read_file_as_binary(path)