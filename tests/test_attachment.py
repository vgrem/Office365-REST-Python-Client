import os.path

from office365.sharepoint.attachment_file_creation_information import AttachmentFileCreationInformation
from tests.sharepoint_case import SPTestCase


class TestListItem(SPTestCase):
    target_list = None
    target_item = None
    source_path = "{}/../examples/data/binary".format(os.path.dirname(__file__))
    filename = 'test.bin'
    with open(source_path, 'rb') as content_file:
        file_content = content_file.read()

    def setUp(self):
        self.target_list = self.context.web.lists.get_by_title("TestContact")
        item_properties = {'Title': 'Test Attachment Contact'}
        self.target_item = self.target_list.add_item(item_properties)
        self.context.execute_query()

    def tearDown(self):
        self.target_item.delete_object()
        self.context.execute_query()

    def test_1_add_attachment(self):
        attachment_file_information = AttachmentFileCreationInformation(self.filename, self.file_content)

        created_file = self.target_item.attachment_files.add(attachment_file_information)
        self.context.execute_query()
        print('Attachment \'{0}\' has been created.'.format(created_file.properties["FileName"]))
