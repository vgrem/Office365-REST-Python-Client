from tests import random_seed
from tests.sharepoint_case import SPTestCase
from office365.sharepoint.list_creation_information import ListCreationInformation
from office365.sharepoint.list_template_type import ListTemplateType
from tests.test_methods import ensure_list


class TestSharePointListItem(SPTestCase):
    target_list = None

    @classmethod
    def setUpClass(cls):
        super(TestSharePointListItem, cls).setUpClass()
        cls.target_list = ensure_list(cls.client.web,
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
        cls.client.execute_query()

    def test1_create_list_item(self):
        item_properties = {'Title': self.target_item_properties["Title"],
                           '__metadata': {'type': 'SP.Data.TasksListItem'}}
        item = self.target_list.add_item(item_properties)
        self.client.execute_query()
        self.assertIsNotNone(item.properties["Title"])
        self.target_item_properties["Id"] = item.properties["Id"]

    def test2_get_list_item(self):
        item = self.target_list.get_item_by_id(self.target_item_properties["Id"])
        self.client.load(item)
        self.client.execute_query()
        self.assertIsNotNone(item.properties["Id"])

    def test3_update_listItem(self):
        item_to_update = self.target_list.get_item_by_id(self.target_item_properties["Id"])
        self.client.load(item_to_update)
        self.client.execute_query()
        last_updated = item_to_update.properties['Modified']

        new_title = "Task item %s" % random_seed
        item_to_update.set_property('Title', new_title)
        item_to_update.update()
        self.client.load(item_to_update)  # retrieve updated
        self.client.execute_query()
        self.assertNotEqual(item_to_update.properties["Modified"], last_updated)
        self.assertEqual(item_to_update.properties["Title"], new_title)

    def test4_systemUpdate_listItem(self):
        item_to_update = self.target_list.get_item_by_id(self.target_item_properties["Id"])
        self.client.load(item_to_update)
        self.client.execute_query()
        last_updated = item_to_update.properties['Modified']

        new_title = "Task item %s" % random_seed
        item_to_update.set_property('Title', new_title)
        item_to_update.system_update()
        self.client.load(item_to_update)  # retrieve updated
        self.client.execute_query()
        self.assertEqual(item_to_update.properties["Modified"], last_updated)
        self.assertEqual(item_to_update.properties["Title"], new_title)

    def test5_delete_list_item(self):
        item = self.target_list.get_item_by_id(self.target_item_properties["Id"])
        item.delete_object()
        self.client.execute_query()

        result = self.target_list.get_items().filter("Id eq {0}".format(self.target_item_properties["Id"]))
        self.client.load(result)
        self.client.execute_query()
        self.assertEqual(0, len(result))
