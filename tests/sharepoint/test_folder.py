from random import randint

from tests import create_unique_name
from tests.sharepoint.sharepoint_case import SPTestCase

from office365.sharepoint.changes.change_collection import ChangeCollection
from office365.sharepoint.folders.folder import Folder
from office365.sharepoint.lists.list import List
from office365.sharepoint.lists.list_creation_information import ListCreationInformation
from office365.sharepoint.lists.list_template_type import ListTemplateType


class TestSharePointFolder(SPTestCase):
    target_folder_name = "Archive_" + str(randint(0, 1000))
    target_list = None  # type: List
    target_folder = None  # type: Folder
    deleted_folder_guid = None

    @classmethod
    def setUpClass(cls):
        super(TestSharePointFolder, cls).setUpClass()
        cls.target_list = cls.ensure_list(cls.client.web,
                                          ListCreationInformation(
                                              create_unique_name("Documents"),
                                              None,
                                              ListTemplateType.DocumentLibrary))

    @classmethod
    def tearDownClass(cls):
        cls.target_list.delete_object().execute_query()

    def test1_enum_folders_and_files(self):
        parent_folder = self.__class__.target_list.root_folder.get().execute_query()
        self.assertIsNotNone(parent_folder.serverRelativeUrl)

        folder_url = parent_folder.serverRelativeUrl
        folder_object = self.client.web.get_folder_by_server_relative_url(folder_url).get().execute_query()
        self.assertTrue(folder_object.serverRelativeUrl, folder_url)
        folders = folder_object.folders.get().execute_query()
        for child_folder in folders:
            self.assertIsNotNone(child_folder.resource_path)
            files = child_folder.files.get().execute_query()
            for file_in_folder in files:
                self.assertIsNotNone(file_in_folder.resource_path)

    def test2_create_folder(self):
        folder_new = self.__class__.target_list.root_folder.folders.add(self.__class__.target_folder_name)\
            .execute_query()
        self.assertTrue(folder_new.exists)
        self.__class__.target_folder = folder_new

    def test4_get_folder_by_id(self):
        folder_id = self.__class__.target_folder.unique_id
        folder = self.client.web.get_folder_by_id(folder_id).execute_query()
        self.assertIsNotNone(folder.resource_path)

    def test5_update_folder_properties(self):
        list_item = self.__class__.target_folder.list_item_all_fields
        list_item.set_property("Title", "New folder title").update().execute_query()

    def test6_upload_file_into_folder(self):
        uploaded_file = self.__class__.target_folder.upload_file("sample.txt", "Some content goes here...")
        self.client.execute_query()
        self.assertIsNotNone(uploaded_file.serverRelativeUrl)

    def test7_get_folder_files(self):
        folder = self.__class__.target_folder
        self.client.load(folder, ["Files"])
        self.client.execute_query()
        self.assertGreater(len(folder.files), 0)

    def test8_copy_folder(self):

        folder_name = "Copy_" + str(randint(0, 10000))
        parent_folder = self.__class__.target_folder.get().execute_query()
        folder_to_url = "/".join([parent_folder.serverRelativeUrl, folder_name])

        # 3. copy folder with files
        folder_to = self.__class__.target_folder.copy_to(folder_to_url)
        self.client.load(folder_to, ["Files"])
        self.client.execute_query()
        self.assertGreater(len(folder_to.files), 0)

    def test9_rename_folder(self):
        folder_to_rename = self.__class__.target_folder
        self.__class__.target_folder_name = "_Archive_" + str(randint(0, 1000))
        target_folder = folder_to_rename.rename(self.__class__.target_folder_name).get().execute_query()
        self.assertEqual(target_folder.name, self.__class__.target_folder_name)

    def test_10_find_folder(self):
        result = self.__class__.target_list.root_folder.folders \
            .filter("Name eq '{0}'".format(self.__class__.target_folder_name)) \
            .get() \
            .execute_query()
        self.assertEqual(len(result), 1)

    def test_11_move_folder(self):
        folder_from = self.__class__.target_folder.get().execute_query()
        folder_name = "Move_" + str(randint(0, 1000))
        folder_to = self.__class__.target_list.root_folder.add(folder_name).execute_query()

        folder_to = folder_from.move_to(folder_to.serverRelativeUrl).get().execute_query()
        self.assertIsNotNone(folder_to.serverRelativeUrl)

    def test_12_recycle_folder(self):
        folder_to_recycle = self.__class__.target_folder
        result = folder_to_recycle.recycle().execute_query()
        self.assertIsNotNone(result.value)
        self.__class__.deleted_folder_guid = result.value

    def test_13_restore_folder(self):
        recycle_item = self.client.web.recycle_bin.get_by_id(self.__class__.deleted_folder_guid)
        recycle_item.restore().execute_query()

    def test_14_get_folder_changes(self):
        folder = self.__class__.target_folder
        changes = folder.get_changes().execute_query()
        self.assertIsInstance(changes, ChangeCollection)
        self.assertGreaterEqual(len(changes), 0)

    def test_15_delete_folder(self):
        folder_to_delete = self.__class__.target_folder
        folder_to_delete.delete_object().execute_query()

        result = self.__class__.target_list.root_folder.folders\
            .filter("Name eq '{0}'".format(self.__class__.target_folder_name))\
            .get()\
            .execute_query()
        self.assertEqual(len(result), 0)

    def test_16_add_using_path(self):
        new_folder = self.__class__.target_list.root_folder.folders\
            .add_using_path(self.target_folder_name, True).execute_query()
        self.assertIsNotNone(new_folder.resource_path)
        self.__class__.target_folder = new_folder

    def test_17_get_by_path(self):
        folder = self.__class__.target_list.root_folder.folders.get_by_path(self.target_folder_name).execute_query()
        self.assertIsNotNone(folder.resource_path)
