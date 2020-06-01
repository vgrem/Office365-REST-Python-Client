from random import randint

from office365.sharepoint.move_operations import MoveOperations
from tests import random_seed
from tests.sharepoint.sharepoint_case import SPTestCase
from office365.sharepoint.list_creation_information import ListCreationInformation
from office365.sharepoint.list_template_type import ListTemplateType
from tests.sharepoint.test_methods import ensure_list


class TestSharePointFolder(SPTestCase):
    target_folder_name = "Archive_" + str(randint(0, 1000))
    target_list = None

    @classmethod
    def setUpClass(cls):
        super(TestSharePointFolder, cls).setUpClass()
        cls.target_list = ensure_list(cls.client.web,
                                      ListCreationInformation(
                                          "Documents %s" % random_seed,
                                          None,
                                          ListTemplateType.DocumentLibrary))

    @classmethod
    def tearDownClass(cls):
        cls.target_list.delete_object()
        cls.client.execute_query()

    def test1_enum_folders_and_files(self):
        parent_folder = self.__class__.target_list.rootFolder
        self.client.load(parent_folder)
        self.client.execute_query()
        self.assertIsNotNone(parent_folder.properties["ServerRelativeUrl"])

        folder_url = parent_folder.properties["ServerRelativeUrl"]
        folder_object = self.client.web.get_folder_by_server_relative_url(folder_url)
        self.client.load(folder_object)
        self.client.execute_query()
        self.assertTrue(folder_object.properties["ServerRelativeUrl"], folder_url)
        folders = folder_object.folders
        self.client.load(folders)
        self.client.execute_query()
        for child_folder in folders:
            self.assertIsNotNone(child_folder.resource_path)
            self.assertIsNotNone(child_folder.resource_path)
            files = child_folder.files
            self.client.load(files)
            self.client.execute_query()
            for file_in_folder in files:
                self.assertIsNotNone(file_in_folder.resource_path)

    def test2_create_folder(self):
        folder_new = self.__class__.target_list.rootFolder.folders.add(self.__class__.target_folder_name)
        self.client.execute_query()
        self.assertTrue(folder_new.properties["Exists"])

    def test4_update_folder(self):
        folder_to_update = self.__class__.target_list.rootFolder.folders.get_by_url(self.__class__.target_folder_name)
        self.__class__.target_folder_name = "_Archive_" + str(randint(0, 1000))
        folder_to_update.rename(self.__class__.target_folder_name)
        self.client.execute_query()

        result = self.__class__.target_list.rootFolder.folders.filter("Name eq '{0}'".format(self.__class__.target_folder_name))
        self.client.load(result)
        self.client.execute_query()
        self.assertEqual(len(result), 1)

    def test5_copy_folder(self):
        folder_to_copy = self.__class__.target_list.rootFolder.folders.get_by_url(self.__class__.target_folder_name)
        # 1.make sure a source folder contains at least one file
        uploaded_file = folder_to_copy.upload_file("sample.txt", "Some content goes here...")
        self.client.load(folder_to_copy, ["Files"])
        self.client.execute_query()
        self.assertIsNotNone(uploaded_file.properties['ServerRelativeUrl'])
        self.assertGreater(len(folder_to_copy.files), 0)

        # 2.ensure a target folder exists
        folder_name = "Copy_" + str(randint(0, 1000))
        folder_to = self.__class__.target_list.rootFolder.add(folder_name)
        self.client.execute_query()
        self.assertIsNotNone(folder_to.properties['ServerRelativeUrl'])

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
        self.assertIsNotNone(folder_to.properties['ServerRelativeUrl'])

        folder.moveto(folder_to.properties['ServerRelativeUrl'], MoveOperations.overwrite)
        self.client.execute_query()
        self.assertIsNotNone(folder_to.properties['ServerRelativeUrl'])

    def test7_delete_folder(self):
        folder_to_delete = self.__class__.target_list.rootFolder.folders.get_by_url(self.__class__.target_folder_name)
        folder_to_delete.delete_object()
        self.client.execute_query()

        result = self.__class__.target_list.rootFolder.folders.filter("Name eq '{0}'".format(self.__class__.target_folder_name))
        self.client.load(result)
        self.client.execute_query()
        self.assertEqual(len(result), 0)
