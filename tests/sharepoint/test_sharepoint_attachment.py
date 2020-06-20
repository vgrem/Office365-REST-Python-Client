import os.path
from tests.sharepoint.sharepoint_case import SPTestCase
from office365.sharepoint.attachments.attachmentfile_creation_information import AttachmentfileCreationInformation
from office365.sharepoint.lists.list_creation_information import ListCreationInformation
from office365.sharepoint.lists.list_template_type import ListTemplateType


class TestListItemAttachment(SPTestCase):
    attachment_file_name = "SharePoint User Guide.docx"
    target_item = None

    @classmethod
    def setUpClass(cls):
        super(TestListItemAttachment, cls).setUpClass()
        cls.target_list = cls.ensure_list(cls.client.web,
                                          ListCreationInformation("Tasks",
                                                                  None,
                                                                  ListTemplateType.Tasks))
        item_properties = {'Title': 'Approval Task'}
        cls.target_item = cls.target_list.add_item(item_properties)
        cls.client.execute_query()

    @classmethod
    def tearDownClass(cls):
        cls.target_item.delete_object()
        cls.client.execute_query()

    def test1_add_attachment(self):
        file_content = self.read_attachment_test_file()
        attachment_file_information = AttachmentfileCreationInformation(self.attachment_file_name, file_content)
        created_file = self.__class__.target_item.attachmentFiles.add(attachment_file_information)
        self.client.execute_query()
        self.assertIsNotNone(created_file.properties["FileName"])

    def test2_list_attachments(self):
        attachment_files = self.__class__.target_item.attachmentFiles
        self.client.load(attachment_files)
        self.client.execute_query()

        attachment_files_items = list(attachment_files)
        self.assertEqual(len(attachment_files_items), 1)
        self.assertEqual(attachment_files_items[0].properties['FileName'], self.attachment_file_name)

    def test3_read_attachments(self):
        attachment_file = self.__class__.target_item.attachmentFiles.get_by_filename(self.attachment_file_name)
        self.client.load(attachment_file)
        self.client.execute_query()
        data = attachment_file.read()

        file_content = self.read_attachment_test_file()
        self.assertEqual(data, file_content)

    def test4_update_attachments(self):
        attachment_file = self.__class__.target_item.attachmentFiles.get_by_filename(self.attachment_file_name)
        self.client.load(attachment_file)
        self.client.execute_query()

        updated_data = os.urandom(1024)
        attachment_file.write(updated_data)

        self.client.load(attachment_file)
        self.client.execute_query()

        data = attachment_file.read()

        self.assertEqual(data, updated_data)

    def test5_delete_attachments(self):
        attachment_file = self.__class__.target_item.attachmentFiles.get_by_filename(self.attachment_file_name)
        self.client.load(attachment_file)
        self.client.execute_query()

        attachment_file.delete_object()
        self.client.execute_query()

        attachment_files = self.__class__.target_item.attachmentFiles
        self.client.load(attachment_files)
        self.client.execute_query()
        attachment_files_items = list(attachment_files)

        self.assertEqual(len(attachment_files_items), 0)

    def read_attachment_test_file(self):
        path = "{0}/../data/{1}".format(os.path.dirname(__file__), self.attachment_file_name)
        with open(path, 'rb') as content_file:
            file_content = content_file.read()
        return file_content
