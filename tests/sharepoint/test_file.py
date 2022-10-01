import os

from tests import test_client_credentials, create_unique_name, test_root_site_url
from tests.sharepoint.sharepoint_case import SPTestCase

from office365.sharepoint.changes.query import ChangeQuery
from office365.sharepoint.files.file import File
from office365.sharepoint.lists.list import List
from office365.sharepoint.lists.creation_information import ListCreationInformation
from office365.sharepoint.lists.template_type import ListTemplateType
from office365.sharepoint.pages.template_file_type import TemplateFileType
from office365.sharepoint.webs.web import Web


def normalize_response(response):
    content = response.decode("utf-8")
    if (content[0] == content[-1]) and content.startswith(("'", '"')):
        return content[1:-1]
    return content


class TestSharePointFile(SPTestCase):
    content_placeholder = create_unique_name("1234567890 abcdABCD")
    file_entries = [
        {"Name": "Sample.txt", "Type": "Text"},
        {"Name": "SharePoint User Guide.docx", "Type": "Binary"}
    ]
    target_list = None  # type: List
    target_file = None  # type: File

    @classmethod
    def setUpClass(cls):
        super(TestSharePointFile, cls).setUpClass()
        cls.target_list = cls.ensure_list(cls.client.web,
                                          ListCreationInformation(
                                              create_unique_name("Archive Documents"),
                                              None,
                                              ListTemplateType.DocumentLibrary))

    @classmethod
    def tearDownClass(cls):
        cls.target_list.delete_object().execute_query()

    def test1_upload_files(self):
        for entry in self.file_entries:
            path = "{0}/../data/{1}".format(os.path.dirname(__file__), entry["Name"])
            if entry["Type"] == "Binary":
                file_content = self.read_file_as_binary(path)
            else:
                file_content = self.read_file_as_text(path)
            target_folder = self.__class__.target_list.root_folder
            uploaded_file = target_folder.upload_file(entry["Name"], file_content).execute_query()
            self.assertEqual(uploaded_file.name, entry["Name"])

    def test2_upload_large_file(self):
        path = "{0}/../data/big_buck_bunny.mp4".format(os.path.dirname(__file__))
        file_size = os.path.getsize(path)
        size_1mb = 1000000
        result_file = self.__class__.target_list.root_folder.files.create_upload_session(path, size_1mb).execute_query()
        self.assertEqual(file_size, int(result_file.length))

    def test3_get_first_file(self):
        files = self.__class__.target_list.root_folder.files.top(1).get().execute_query()
        self.assertEqual(len(files), 1)
        self.__class__.target_file = files[0]

    def test4_get_file_from_absolute_url(self):
        file_abs_url = test_root_site_url + self.__class__.target_file.serverRelativeUrl
        file = File.from_url(file_abs_url).with_credentials(test_client_credentials).get().execute_query()
        self.assertIsNotNone(file.serverRelativeUrl)

    def test5_create_file_anon_link(self):
        file_url = self.__class__.target_file.serverRelativeUrl
        result = Web.create_anonymous_link(self.client, file_url, False).execute_query()
        self.assertIsNotNone(result.value)

    def test6_load_file_metadata(self):
        list_item = self.__class__.target_file.listItemAllFields.expand(["File"]).get().execute_query()
        self.assertIsInstance(list_item.file, File)

    def test7_load_file_metadata_alt(self):
        list_item = self.__class__.target_file.listItemAllFields
        self.client.load(list_item, ["File"])
        self.client.execute_query()
        self.assertIsInstance(list_item.file, File)

    def test8_update_file_content(self):
        """Test file upload operation"""
        files = self.__class__.target_list.root_folder.files.get().execute_query()
        for file_upload in files:
            response = File.save_binary(self.client, file_upload.properties["ServerRelativeUrl"],
                                        self.content_placeholder)
            self.assertTrue(response.ok)

    def test9_update_file_metadata(self):
        """Test file update metadata"""
        list_item = self.__class__.target_file.listItemAllFields  # get metadata
        list_item.set_property('Title', 'Updated')
        list_item.update().execute_query()

    def test_10_list_file_versions(self):
        """Test file update metadata"""
        file_with_versions = self.__class__.target_file.expand(["Versions"]).get().execute_query()
        self.assertGreater(len(file_with_versions.versions), 0)

    def test_11_delete_file_version(self):
        versions = self.__class__.target_file.versions.top(1).get().execute_query()
        self.assertEqual(len(versions), 1)
        self.assertIsNotNone(versions[0].resource_path)
        versions[0].delete_object().execute_query()

    def test_12_delete_file_version_by_id(self):
        versions = self.__class__.target_file.versions.top(1).get().execute_query()
        self.assertEqual(len(versions), 1)
        ver_id = versions[0].id
        versions.delete_by_id(ver_id).execute_query()

    def test_13_download_file(self):
        """Test file upload operation"""
        files = self.__class__.target_list.root_folder.files.get().execute_query()
        for file in files:  # type: File
            content = file.read()
            enc_content = normalize_response(content)
            self.assertEqual(enc_content, self.content_placeholder)

    def test_14_copy_file(self):
        files = self.__class__.target_list.root_folder.files.get().execute_query()
        for cur_file in files:  # type: File
            file_url = cur_file.serverRelativeUrl
            path, file_name = os.path.split(file_url)
            new_file_url = '/'.join([path, "copied_" + file_name])
            cur_file.copyto(new_file_url, True).execute_query()

            moved_file = self.client.web.get_file_by_server_relative_url(new_file_url).get().execute_query()
            self.assertEqual(new_file_url, moved_file.serverRelativeUrl)

    def test_15_move_file(self):
        files = self.__class__.target_list.root_folder.files.get().execute_query()
        for cur_file in files:
            file_url = cur_file.properties["ServerRelativeUrl"]
            path, file_name = os.path.split(file_url)
            new_file_url = '/'.join([path, "moved_" + file_name])
            cur_file.moveto(new_file_url, 1).execute_query()

            moved_file = self.client.web.get_file_by_server_relative_url(new_file_url).get().execute_query()
            self.assertEqual(new_file_url, moved_file.properties["ServerRelativeUrl"])

    def test_16_recycle_first_file(self):
        """Test file upload operation"""
        files = self.__class__.target_list.root_folder.files.get().execute_query()
        files_count = len(files)
        if files_count > 0:
            first_file = files[0]
            first_file.recycle()
            first_file.execute_query()
            files_after = self.__class__.target_list.root_folder.files.get().execute_query()
            self.assertEqual(len(files) - 1, len(files_after))

    def test_17_create_template_file(self):
        target_folder = self.__class__.target_list.root_folder.get().execute_query()
        file_url = '/'.join([target_folder.serverRelativeUrl, "WikiPage.aspx"])
        file_new = self.__class__.target_list.root_folder.files.add_template_file(file_url, TemplateFileType.WikiPage)
        self.client.execute_query()
        self.assertEqual(file_new.serverRelativeUrl, file_url)
        self.__class__.target_file = file_new

    def test_18_get_folder_changes(self):
        changes = self.__class__.target_file.listItemAllFields.get_changes(ChangeQuery(item=True)).execute_query()
        self.assertGreater(len(changes), 0)

    def test_19_delete_files(self):
        files_to_delete = self.__class__.target_list.root_folder.files.get().execute_query()
        for file_to_delete in files_to_delete:  # type: File
            file_to_delete.delete_object().execute_query()

        file_col = self.__class__.target_list.root_folder.files.get().execute_query()
        self.assertEqual(len(file_col), 0)


