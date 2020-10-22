from random import randint

from tests import random_seed
from tests.sharepoint.sharepoint_case import SPTestCase

from office365.sharepoint.changes.change_collection import ChangeCollection
from office365.sharepoint.changes.change_query import ChangeQuery
from office365.sharepoint.files.move_operations import MoveOperations
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
                                              "Documents %s" % random_seed,
                                              None,
                                              ListTemplateType.DocumentLibrary))

    @classmethod
    def tearDownClass(cls):
        cls.target_list.delete_object().execute_query()

    def test1_enum_folders_and_files(self):
        parent_folder = self.__class__.target_list.rootFolder.get().execute_query()
        self.assertIsNotNone(parent_folder.serverRelativeUrl)

        folder_url = parent_folder.serverRelativeUrl
        folder_object = self.client.web.get_folder_by_server_relative_url(folder_url).get().execute_query()
        self.assertTrue(folder_object.properties["ServerRelativeUrl"], folder_url)
        folders = folder_object.folders.get().execute_query()
        for child_folder in folders:
            self.assertIsNotNone(child_folder.resource_path)
            files = child_folder.files.get().execute_query()
            for file_in_folder in files:
                self.assertIsNotNone(file_in_folder.resource_path)

    def test2_create_folder(self):
        folder_new = self.__class__.target_list.rootFolder.folders.add(self.__class__.target_folder_name).execute_query()
        self.assertTrue(folder_new.properties["Exists"])
        self.__class__.target_folder = folder_new

    def test3_get_folder_by_id(self):
        folder_id = self.__class__.target_folder.properties['UniqueId']
        folder = self.client.web.get_folder_by_id(folder_id).execute_query()
        self.assertIsNotNone(folder.resource_path)

    def test4_update_folder(self):
        folder_to_update = self.__class__.target_list.rootFolder.folders.get_by_url(self.__class__.target_folder_name)
        self.__class__.target_folder_name = "_Archive_" + str(randint(0, 1000))
        folder_to_update.rename(self.__class__.target_folder_name).execute_query()

        result = self.__class__.target_list.rootFolder.folders\
            .filter("Name eq '{0}'".format(self.__class__.target_folder_name))\
            .get()\
            .execute_query()
        self.assertEqual(len(result), 1)

    def test5_copy_folder(self):
        folder_to_copy = self.__class__.target_list.rootFolder.folders.get_by_url(self.__class__.target_folder_name)
        # 1.make sure a source folder contains at least one file
        uploaded_file = folder_to_copy.upload_file("sample.txt", "Some content goes here...")
        self.client.load(folder_to_copy, ["Files"])
        self.client.execute_query()
        self.assertIsNotNone(uploaded_file.serverRelativeUrl)
        self.assertGreater(len(folder_to_copy.files), 0)

        # 2.ensure a target folder exists
        folder_name = "Copy_" + str(randint(0, 1000))
        folder_to = self.__class__.target_list.rootFolder.add(folder_name)
        self.client.execute_query()
        self.assertIsNotNone(folder_to.serverRelativeUrl)

        # 3. copy folder with files
        folder_to_copy.copyto(folder_to.properties['ServerRelativeUrl'], True)
        self.client.load(folder_to, ["Files"])
        self.client.execute_query()
        self.assertGreater(len(folder_to.files), 0)

    def test6_move_folder(self):
        folder = self.__class__.target_list.rootFolder.folders.get_by_url(self.__class__.target_folder_name)
        folder_name = "Move_" + str(randint(0, 1000))
        folder_to = self.__class__.target_list.rootFolder.add(folder_name)
        self.client.execute_query()
        self.assertIsNotNone(folder_to.serverRelativeUrl)

        folder.moveto(folder_to.properties['ServerRelativeUrl'], MoveOperations.overwrite)
        self.client.execute_query()
        self.assertIsNotNone(folder_to.serverRelativeUrl)

    def test7_recycle_folder(self):
        folder_to_recycle = self.__class__.target_list.rootFolder.folders.get_by_url(self.__class__.target_folder_name)
        result = folder_to_recycle.recycle()
        self.client.execute_query()
        self.assertIsNotNone(result.value)
        self.__class__.deleted_folder_guid = result.value

    def test8_restore_folder(self):
        recycle_item = self.client.web.recycleBin.get_by_id(self.__class__.deleted_folder_guid)
        recycle_item.restore().execute_query()

    def test_10_get_folder_changes(self):
        folder = self.__class__.target_list.rootFolder.folders.get_by_url(self.__class__.target_folder_name)
        changes = folder.list_item_all_fields.get_changes(ChangeQuery(item=True)).execute_query()
        self.assertIsInstance(changes, ChangeCollection)
        self.assertGreater(len(changes), 0)

    def test_11_delete_folder(self):
        folder_to_delete = self.__class__.target_list.rootFolder.folders.get_by_url(self.__class__.target_folder_name)
        folder_to_delete.delete_object().execute_query()

        result = self.__class__.target_list.rootFolder.folders\
            .filter("Name eq '{0}'".format(self.__class__.target_folder_name))\
            .get()\
            .execute_query()
        self.assertEqual(len(result), 0)
