from random import randint
from tests.sharepoint_case import SPTestCase


class TestFolder(SPTestCase):
    def test_1_create_folder(self):
        target_list = self.context.web.lists.get_by_title("Documents")
        folder_name = "Archive_" + str(randint(0, 1000))
        folder_new = target_list.root_folder.folders.add(folder_name)
        self.context.execute_query()
        self.assertTrue(folder_new.properties["Exists"])


