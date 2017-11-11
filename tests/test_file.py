import os

from office365.sharepoint.list_creation_information import ListCreationInformation
from office365.sharepoint.list_template_type import ListTemplateType
from tests import random_seed
from tests.sharepoint_case import SPTestCase
from tests.test_utilities import ListExtensions, FileExtensions, read_file_as_binary, read_file_as_text, \
    normalize_response


class TestFile(SPTestCase):
    content_placeholder = "1234567890 abcdABCD %s" % random_seed
    file_entries = [
        {"Name": "Sample.txt", "Type": "Text"},
        {"Name": "SharePoint User Guide.docx", "Type": "Binary"}
    ]

    @classmethod
    def setUpClass(cls):
        super(TestFile, cls).setUpClass()
        cls.target_list = ListExtensions.ensure_list(cls.context.web,
                                                     ListCreationInformation(
                                                         "Archive Documents N%s" % random_seed,
                                                         None,
                                                         ListTemplateType.DocumentLibrary))

    @classmethod
    def tearDownClass(cls):
        cls.target_list.delete_object()
        cls.context.execute_query()

    def test_1_upload_file(self):
        for entry in self.file_entries:
            path = "{0}/data/{1}".format(os.path.dirname(__file__), entry["Name"])
            if entry["Type"] == "Binary":
                file_content = read_file_as_binary(path)
            else:
                file_content = read_file_as_text(path)
            upload_file = FileExtensions.upload_file(self.target_list, entry["Name"], file_content)
            self.assertEqual(upload_file.properties["Name"], entry["Name"])

    def test_2_list_files(self):
        files = self.target_list.root_folder.files
        self.context.load(files)
        self.context.execute_query()
        files_items = list(files)
        self.assertEqual(len(files_items), 2)

    def test_3_update_file(self):
        """Test file upload operation"""
        files = self.target_list.root_folder.files
        self.context.load(files)
        self.context.execute_query()
        for file_upload in files:
            file_upload.write(self.content_placeholder)

    def test_4_download_file(self):
        """Test file upload operation"""
        files = self.target_list.root_folder.files
        self.context.load(files)
        self.context.execute_query()
        for file_download in files:
            content = file_download.read()
            enc_content = normalize_response(content)
            self.assertEqual(enc_content, self.content_placeholder)

    def test_5_delete_file(self):
        files_to_delete = self.target_list.root_folder.files
        self.context.load(files_to_delete)
        self.context.execute_query()
        for file_to_delete in files_to_delete:
            file_to_delete.delete_object()
            self.context.execute_query()

        # verify
        result = self.target_list.root_folder.files
        self.context.load(result)
        self.context.execute_query()
        files_items = list(result)
        self.assertEqual(len(files_items), 0)

