import os

from office365.sharepoint.file import File
from tests import random_seed
from tests.sharepoint.sharepoint_case import SPTestCase
from tests.sharepoint.test_methods import (
    read_file_as_binary,
    read_file_as_text,
    ensure_list)

from office365.sharepoint.list_creation_information import ListCreationInformation
from office365.sharepoint.list_template_type import ListTemplateType
from office365.sharepoint.template_file_type import TemplateFileType


def normalize_response(response):
    content = response.decode("utf-8")
    if (content[0] == content[-1]) and content.startswith(("'", '"')):
        return content[1:-1]
    return content


class TestSharePointFile(SPTestCase):
    content_placeholder = "1234567890 abcdABCD %s" % random_seed
    file_entries = [
        {"Name": "Sample.txt", "Type": "Text"},
        {"Name": "SharePoint User Guide.docx", "Type": "Binary"}
    ]
    target_list = None
    target_file = None

    @classmethod
    def setUpClass(cls):
        super(TestSharePointFile, cls).setUpClass()
        cls.target_list = ensure_list(cls.client.web,
                                      ListCreationInformation(
                                          "Archive Documents N%s" % random_seed,
                                          None,
                                          ListTemplateType.DocumentLibrary))

    @classmethod
    def tearDownClass(cls):
        cls.target_list.delete_object()
        cls.client.execute_query()

    def test1_upload_file(self):
        for entry in self.file_entries:
            path = "{0}/../data/{1}".format(os.path.dirname(__file__), entry["Name"])
            if entry["Type"] == "Binary":
                file_content = read_file_as_binary(path)
            else:
                file_content = read_file_as_text(path)
            uploaded_file = self.__class__.target_list.rootFolder.upload_file(entry["Name"], file_content)
            self.client.execute_query()
            self.assertEqual(uploaded_file.properties["Name"], entry["Name"])

    def test2_list_files(self):
        files = self.__class__.target_list.rootFolder.files.top(1)
        self.client.load(files)
        self.client.execute_query()
        files_items = list(files)
        self.assertEqual(len(files_items), 1)
        first_item = files[0].listItemAllFields
        self.client.load(first_item, ["File"])
        self.client.execute_query()
        self.assertIsNotNone(first_item.file)

    def test3_update_file_content(self):
        """Test file upload operation"""
        files = self.__class__.target_list.rootFolder.files
        self.client.load(files)
        self.client.execute_query()
        for file_upload in files:
            response = File.save_binary(self.client, file_upload.properties["ServerRelativeUrl"],
                                        self.content_placeholder)
            self.assertTrue(response.ok)

    def test4_update_file_metadata(self):
        """Test file update metadata"""
        files = self.__class__.target_list.rootFolder.files.top(1)
        self.client.load(files)
        self.client.execute_query()
        first_file = files[0]
        self.__class__.target_file = first_file
        list_item = first_file.listItemAllFields  # get metadata
        list_item.set_property('Title', 'Updated')
        list_item.update()
        self.client.execute_query()

    def test5_get_file_versions(self):
        """Test file update metadata"""
        file_with_versions = self.__class__.target_file.expand(["Versions"])
        self.client.load(file_with_versions)
        self.client.execute_query()
        self.assertGreater(len(file_with_versions.versions), 0)

    def test6_download_file(self):
        """Test file upload operation"""
        files = self.__class__.target_list.rootFolder.files
        self.client.load(files)
        self.client.execute_query()
        for file_download in files:
            content = file_download.read()
            enc_content = normalize_response(content)
            self.assertEqual(enc_content, self.content_placeholder)

    def test7_copy_file(self):
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

    def test8_move_file(self):
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

    def test9_recycle_first_file(self):
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

    def test10_create_template_file(self):
        target_folder = self.__class__.target_list.rootFolder
        self.client.load(target_folder)
        self.client.execute_query()
        file_url = '/'.join([target_folder.properties["ServerRelativeUrl"], "WikiPage.aspx"])
        file_new = self.__class__.target_list.rootFolder.files.add_template_file(file_url, TemplateFileType.WikiPage)
        self.client.execute_query()
        self.assertEqual(file_new.properties["ServerRelativeUrl"], file_url)

    def test11_delete_file(self):
        files_to_delete = self.__class__.target_list.rootFolder.files
        self.client.load(files_to_delete)
        self.client.execute_query()
        for file_to_delete in files_to_delete:
            file_to_delete.delete_object()
            self.client.execute_query()

        result = self.__class__.target_list.rootFolder.files
        self.client.load(result)
        self.client.execute_query()
        files_items = list(result)
        self.assertEqual(len(files_items), 0)
