import os.path

from office365.sharepoint.attachmentfile_creation_information import AttachmentfileCreationInformation
from tests.sharepoint_case import SPTestCase


class TestListItem(SPTestCase):
    target_list = None
    target_item = None
    source_path = "{}/data/binary".format(os.path.dirname(__file__))
    filename = 'test.bin'
    with open(source_path, 'rb') as content_file:
        file_content = content_file.read()

    @classmethod
    def setUpClass(cls):
        super(TestListItem, cls).setUpClass()
        cls.target_list = cls.context.web.lists.get_by_title("TestContact")
        item_properties = {'Title': 'Test Attachment Contact'}
        cls.target_item = cls.target_list.add_item(item_properties)
        cls.context.execute_query()

    @classmethod
    def tearDownClass(cls):
        cls.target_item.delete_object()
        cls.context.execute_query()

    def test_1_add_attachment(self):
        attachment_file_information = AttachmentfileCreationInformation(self.filename, self.file_content)

        created_file = self.target_item.attachment_files.add(attachment_file_information)
        self.context.execute_query()
        print('Attachment \'{0}\' has been created.'.format(created_file.properties["FileName"]))

    def test_2_list_attachments(self):
        attachment_files = self.target_item.attachment_files
        self.context.load(attachment_files)
        self.context.execute_query()

        attachment_files_items = list(attachment_files)
        self.assertEqual(len(attachment_files_items), 1)
        self.assertEqual(attachment_files_items[0].properties['FileName'], self.filename)

    def test_3_read_attachments(self):
        attachment_file = self.target_item.attachment_files.get_by_filename(self.filename)
        self.context.load(attachment_file)
        self.context.execute_query()
        data = attachment_file.read()

        self.assertEqual(data, self.file_content)

    def test_4_update_attachments(self):
        attachment_file = self.target_item.attachment_files.get_by_filename(self.filename)
        self.context.load(attachment_file)
        self.context.execute_query()

        updated_data = os.urandom(1024)
        attachment_file.write(updated_data)

        self.context.load(attachment_file)
        self.context.execute_query()

        data = attachment_file.read()

        self.assertEqual(data, updated_data)

    def test_5_delete_attachments(self):
        attachment_file = self.target_item.attachment_files.get_by_filename(self.filename)
        self.context.load(attachment_file)
        self.context.execute_query()

        attachment_file.delete_object()
        self.context.execute_query()

        attachment_files = self.target_item.attachment_files
        self.context.load(attachment_files)
        self.context.execute_query()
        attachment_files = attachment_files
        attachment_files_items = list(attachment_files)

        self.assertEqual(len(attachment_files_items), 0)
