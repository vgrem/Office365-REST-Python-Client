from random import randint
from tests import random_seed
from tests.sharepoint_case import SPTestCase
from office365.sharepoint.list_creation_information import ListCreationInformation
from office365.sharepoint.list_template_type import ListTemplateType
from tests.test_methods import ensure_list


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
        # cls.context.execute_query()

    def test_enum_folders_and_files(self):
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
            self.assertIsNotNone(child_folder.resourceUrl)
            self.assertIsNotNone(child_folder.resourcePath)
            files = child_folder.files
            self.client.load(files)
            self.client.execute_query()
            for file_in_folder in files:
                self.assertIsNotNone(file_in_folder.resourceUrl)

    def test_1_create_folder(self):
        folder_new = self.__class__.target_list.rootFolder.folders.add(self.target_folder_name)
        self.client.execute_query()
        self.assertTrue(folder_new.properties["Exists"])

    def test_2_update_folder(self):
        folder_to_update = self.__class__.target_list.rootFolder.folders.get_by_url(self.target_folder_name)
        new_folder_name = "_Archive_" + str(randint(0, 1000))
        folder_to_update.set_property("Name", new_folder_name)
        folder_to_update.update()
        self.client.execute_query()

        # result = self.target_list.root_folder.folders.filter("Name eq '{0}'".format(new_folder_name))
        # self.context.load(result)
        # self.context.execute_query()
        # self.assertEqual(len(result), 1)

    def test_3_delete_folder(self):
        folder_to_delete = self.__class__.target_list.rootFolder.folders.get_by_url(self.target_folder_name)
        folder_to_delete.delete_object()
        self.client.execute_query()

        result = self.__class__.target_list.rootFolder.folders.filter("Name eq '{0}'".format(self.target_folder_name))
        self.client.load(result)
        self.client.execute_query()
        self.assertEqual(len(result), 0)
