from random import randint
from tests.sharepoint_case import SPTestCase


class TestFolder(SPTestCase):
    target_folder_name = "Archive_" + str(randint(0, 1000))
    target_list = None

    def setUp(self):
        self.target_list = self.context.web.lists.get_by_title("Documents")

    def test_1_create_folder(self):
        folder_new = self.target_list.root_folder.folders.add(self.target_folder_name)
        self.context.execute_query()
        self.assertTrue(folder_new.properties["Exists"])

    def test_2_update_folder(self):
        folder_to_update = self.target_list.root_folder.folders.get_by_url(self.target_folder_name)
        new_folder_name = "_Archive_" + str(randint(0, 1000))
        folder_to_update.properties["Name"] = new_folder_name
        folder_to_update.update()
        self.context.execute_query()

        #result = self.target_list.root_folder.folders.filter("Name eq '{0}'".format(new_folder_name))
        #self.context.load(result)
        #self.context.execute_query()
        #self.assertEquals(len(result), 1)

    def test_3_delete_folder(self):
        folder_to_delete = self.target_list.root_folder.folders.get_by_url(self.target_folder_name)
        folder_to_delete.delete_object()
        self.context.execute_query()

        result = self.target_list.root_folder.folders.filter("Name eq '{0}'".format(self.target_folder_name))
        self.context.load(result)
        self.context.execute_query()
        self.assertEquals(len(result), 0)
