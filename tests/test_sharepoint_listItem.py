from tests import random_seed
from tests.sharepoint_case import SPTestCase
from tests.test_utilities import ListExtensions

from office365.sharepoint.list_creation_information import ListCreationInformation
from office365.sharepoint.list_template_type import ListTemplateType


class TestListItem(SPTestCase):

    @classmethod
    def setUpClass(cls):
        super(TestListItem, cls).setUpClass()
        cls.target_list = ListExtensions.ensure_list(cls.context.web,
                                                     ListCreationInformation("Tasks",
                                                                             None,
                                                                             ListTemplateType.Tasks)
                                                     )
        cls.target_item_properties = {
            "Title": "Task %s" % random_seed,
            "Id": None
        }

    @classmethod
    def tearDownClass(cls):
        cls.target_list.delete_object()
        cls.context.execute_query()

    def test_1_create_list_item(self):
        item_properties = {'Title': self.target_item_properties["Title"], '__metadata': {'type': 'SP.Data.TasksListItem'}}
        item = self.target_list.add_item(item_properties)
        self.context.execute_query()
        self.assertIsNotNone(item.properties["Title"])
        self.target_item_properties["Id"] = item.properties["Id"]

    def test_2_delete_list_item(self):
        item = self.target_list.get_item_by_id(self.target_item_properties["Id"])
        item.delete_object()
        self.context.execute_query()

        result = self.target_list.get_items().filter("Id eq {0}".format(self.target_item_properties["Id"]))
        self.context.load(result)
        self.context.execute_query()
        self.assertEqual(0, len(result))
