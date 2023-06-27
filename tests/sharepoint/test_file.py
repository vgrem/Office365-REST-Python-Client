import os
from io import BytesIO

from office365.sharepoint.changes.query import ChangeQuery
from office365.sharepoint.files.file import File
from office365.sharepoint.folders.folder import Folder
from tests import test_client_credentials
from tests.sharepoint.sharepoint_case import SPTestCase


class TestSharePointFile(SPTestCase):
    parent_folder = None  # type: Folder
    target_file = None  # type: File
    deleted_file_guid = None
    text_content = b"updated content goes here..."

    @classmethod
    def setUpClass(cls):
        super(TestSharePointFile, cls).setUpClass()
        cls.parent_folder = cls.client.web.default_document_library().root_folder

    def test1_upload_file_as_content(self):
        path = "{0}/../data/Sample.txt".format(os.path.dirname(__file__))
        uploaded_file = self.parent_folder.files.upload(path).execute_query()
        self.assertEqual(uploaded_file.name, os.path.basename(path))
        self.assertIsNotNone(uploaded_file.resource_path)
        self.__class__.target_file = uploaded_file

    def test3_get_first_file(self):
        files = self.parent_folder.files.top(1).get().execute_query()
        self.assertEqual(len(files), 1)

    def test4_get_file_from_absolute_url(self):
        result = self.__class__.target_file.get_absolute_url().execute_query()
        file = File.from_url(result.value).with_credentials(test_client_credentials).get().execute_query()
        self.assertIsNotNone(file.serverRelativeUrl)

    def test5_create_file_anon_link(self):
        result = self.__class__.target_file.create_anonymous_link(False).execute_query()
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
        file = self.__class__.target_file.save_binary_stream(self.text_content).execute_query()
        self.assertTrue(file.resource_path)

    def test9_update_file_metadata(self):
        list_item = self.__class__.target_file.listItemAllFields  # get metadata
        list_item.set_property('Title', 'Updated')
        list_item.update().execute_query()

    def test_10_list_file_versions(self):
        file = self.__class__.target_file.expand(["Versions"]).get().execute_query()
        self.assertGreater(len(file.versions), 0)

    def test_11_delete_file_version(self):
        versions = self.__class__.target_file.versions.top(1).get().execute_query()
        self.assertEqual(len(versions), 1)
        self.assertIsNotNone(versions[0].resource_path)
        versions[0].delete_object().execute_query()

    def test_13_download_file_content(self):
        result = self.__class__.target_file.get_content().execute_query()
        self.assertEqual(result.value, self.text_content)

    def test_14_download_file_content_alt(self):
        with BytesIO() as f:
            self.__class__.target_file.download(f).execute_query()
            content = f.getvalue()
        self.assertEqual(content, self.text_content)

    def test_15_copy_file(self):
        file = self.__class__.target_file.get().execute_query()
        file_url = file.serverRelativeUrl
        path, file_name = os.path.split(file_url)
        new_file_url = '/'.join([path, "copied_" + file_name])
        copied_file = file.copyto(new_file_url, True).execute_query()
        self.assertEqual(new_file_url, copied_file.serverRelativeUrl)

    def test_16_move_file(self):
        file = self.__class__.target_file.get().execute_query()
        file_url = file.properties["ServerRelativeUrl"]
        path, file_name = os.path.split(file_url)
        new_file_url = '/'.join([path, "moved_" + file_name])
        moved_file = file.moveto(new_file_url, 1).execute_query()
        self.assertEqual(new_file_url, moved_file.serverRelativeUrl)

    def test_17_recycle_file(self):
        files_before = self.parent_folder.files.get().execute_query()
        file = self.__class__.target_file
        result = file.recycle().execute_query()
        self.assertIsNotNone(result.value)
        files_after = self.parent_folder.files.get().execute_query()
        self.assertEqual(len(files_before) - 1, len(files_after))
        self.__class__.deleted_file_guid = result.value

    def test_18_restore_file(self):
        recycle_item = self.client.web.recycle_bin.get_by_id(self.__class__.deleted_file_guid)
        recycle_item.restore().execute_query()
        self.assertIsNotNone(recycle_item.resource_path)

    #def test_18_create_template_file(self):
    #    file_url = "WikiPage.aspx"
    #    file = self.parent_folder.files.add_template_file(file_url, TemplateFileType.WikiPage).execute_query()
    #    self.assertEqual(file.name, file_url)

    def test_19_get_files_changes(self):
        changes = self.__class__.target_file.listItemAllFields.get_changes(ChangeQuery(item=True)).execute_query()
        self.assertGreater(len(changes), 0)

    def test_20_delete_file(self):
        files_before = self.parent_folder.files.get().execute_query()
        self.assertGreater(len(files_before), 0)
        self.__class__.target_file.delete_object().execute_query()
        files_after = self.parent_folder.files.get().execute_query()
        self.assertEqual(len(files_after), len(files_before)-1)

    def test_22_upload_large_file(self):
        path = "{0}/../data/big_buck_bunny.mp4".format(os.path.dirname(__file__))
        file_size = os.path.getsize(path)
        size_1mb = 1000000
        file = self.parent_folder.files.create_upload_session(path, size_1mb).execute_query()
        self.assertEqual(file_size, int(file.length))
