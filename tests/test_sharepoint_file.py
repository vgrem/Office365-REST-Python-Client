import os

from tests import random_seed
from tests.sharepoint_case import SPTestCase
from tests.test_utilities import (
    FileExtensions,
    ListExtensions,
    normalize_response,
    read_file_as_binary,
    read_file_as_text,
)

from office365.sharepoint.list_creation_information import ListCreationInformation
from office365.sharepoint.list_template_type import ListTemplateType
from office365.sharepoint.template_file_type import TemplateFileType


class TestSharePointFile(SPTestCase):
    content_placeholder = "1234567890 abcdABCD %s" % random_seed
    file_entries = [
        {"Name": "Sample.txt", "Type": "Text"},
        {"Name": "SharePoint User Guide.docx", "Type": "Binary"}
    ]
    target_list = None

    @classmethod
    def setUpClass(cls):
        super(TestSharePointFile, cls).setUpClass()
        cls.target_list = ListExtensions.ensure_list(cls.client.web,
                                                     ListCreationInformation(
                                                         "Archive Documents N%s" % random_seed,
                                                         None,
                                                         ListTemplateType.DocumentLibrary))

    @classmethod
    def tearDownClass(cls):
        cls.target_list.delete_object()
        cls.client.execute_query()

    def test_1_upload_file(self):
        for entry in self.file_entries:
            path = "{0}/data/{1}".format(os.path.dirname(__file__), entry["Name"])
            if entry["Type"] == "Binary":
                file_content = read_file_as_binary(path)
            else:
                file_content = read_file_as_text(path)
            upload_file = FileExtensions.upload_file(self.__class__.target_list, entry["Name"], file_content)
            self.assertEqual(upload_file.properties["Name"], entry["Name"])

    def test_2_list_files(self):
        files = self.__class__.target_list.rootFolder.files
        self.client.load(files)
        self.client.execute_query()
        files_items = list(files)
        self.assertEqual(len(files_items), 2)

    def test_3_update_file(self):
        """Test file upload operation"""
        files = self.__class__.target_list.rootFolder.files
        self.client.load(files)
        self.client.execute_query()
        for file_upload in files:
            file_upload.write(self.content_placeholder)

    def test_4_download_file(self):
        """Test file upload operation"""
        files = self.__class__.target_list.rootFolder.files
        self.client.load(files)
        self.client.execute_query()
        for file_download in files:
            content = file_download.read()
            enc_content = normalize_response(content)
            self.assertEqual(enc_content, self.content_placeholder)

    def test_5_copy_file(self):
        files = self.__class__.target_list.rootFolder.files
        self.client.load(files)
        self.client.execute_query()
        for cur_file in files:
            file_url = cur_file.properties["ServerRelativeUrl"]
            path, file_name = os.path.split(file_url)
            new_file_url = '/'.join([path, "copied_" + file_name])
            cur_file.copyto(new_file_url, True)
            self.client.execute_query()

            moved_file = self.client.web.get_file_by_server_relative_url(new_file_url)
            self.client.load(moved_file)
            self.client.execute_query()
            self.assertEqual(new_file_url, moved_file.properties["ServerRelativeUrl"])

    def test_6_move_file(self):
        files = self.__class__.target_list.rootFolder.files
        self.client.load(files)
        self.client.execute_query()
        for cur_file in files:
            file_url = cur_file.properties["ServerRelativeUrl"]
            path, file_name = os.path.split(file_url)
            new_file_url = '/'.join([path, "moved_" + file_name])
            cur_file.moveto(new_file_url, 1)
            self.client.execute_query()

            moved_file = self.client.web.get_file_by_server_relative_url(new_file_url)
            self.client.load(moved_file)
            self.client.execute_query()
            self.assertEqual(new_file_url, moved_file.properties["ServerRelativeUrl"])

    def test_7_recycle_first_file(self):
        """Test file upload operation"""
        files = self.__class__.target_list.rootFolder.files
        self.client.load(files)
        self.client.execute_query()
        files_count = len(files)
        if files_count > 0:
            first_file = files[0]
            first_file.recycle()
            self.client.execute_query()
            files_after = self.__class__.target_list.rootFolder.files
            self.client.load(files_after)
            self.client.execute_query()
            self.assertEqual(len(files) - 1, len(files_after))

    def test_8_create_template_file(self):
        target_folder = self.__class__.target_list.rootFolder
        self.client.load(target_folder)
        self.client.execute_query()
        file_url = '/'.join([target_folder.properties["ServerRelativeUrl"], "WikiPage.aspx"])
        file_new = self.__class__.target_list.rootFolder.files.add_template_file(file_url, TemplateFileType.WikiPage)
        self.client.execute_query()
        self.assertEqual(file_new.properties["ServerRelativeUrl"], file_url)

    def test_9_delete_file(self):
        files_to_delete = self.__class__.target_list.rootFolder.files
        self.client.load(files_to_delete)
        self.client.execute_query()
        for file_to_delete in files_to_delete:
            file_to_delete.delete_object()
            self.client.execute_query()

        # verify
        result = self.__class__.target_list.rootFolder.files
        self.client.load(result)
        self.client.execute_query()
        files_items = list(result)
        self.assertEqual(len(files_items), 0)
