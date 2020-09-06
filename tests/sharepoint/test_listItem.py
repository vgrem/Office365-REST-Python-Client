from random import randint
from time import sleep

from tests import random_seed
from tests.sharepoint.sharepoint_case import SPTestCase

from office365.sharepoint.listitems.caml.camlQuery import CamlQuery
from office365.sharepoint.listitems.listitem import ListItem
from office365.sharepoint.lists.list import List
from office365.sharepoint.lists.list_creation_information import ListCreationInformation
from office365.sharepoint.lists.list_template_type import ListTemplateType


class TestSharePointListItem(SPTestCase):
    target_list = None  # type: List
    target_item = None  # type: ListItem

    @classmethod
    def setUpClass(cls):
        super(TestSharePointListItem, cls).setUpClass()
        target_list_title = "Tasks" + str(randint(0, 10000))
        cls.target_list = cls.ensure_list(cls.client.web,
                                          ListCreationInformation(target_list_title,
                                                                  None,
                                                                  ListTemplateType.Tasks)
                                          )
        cls.default_title = "Task %s" % random_seed
        cls.batch_items_count = 3

    @classmethod
    def tearDownClass(cls):
        cls.target_list.delete_object()
        cls.client.execute_query()

    def test1_create_list_item(self):
        item_properties = {'Title': self.default_title}
        new_item = self.target_list.add_item(item_properties)
        self.client.execute_query()
        self.assertIsNotNone(new_item.properties["Title"])
        self.__class__.target_item = new_item

    def test2_enable_folders_in_list(self):
        def _init_list():
            if not self.target_list.enable_folder_creation:
                self.target_list.enable_folder_creation = True
                self.target_list.update()
                self.client.execute_query()
            self.assertTrue(self.target_list.enable_folder_creation, "Folder creation enabled")

        self.target_list.ensure_property("EnableFolderCreation", _init_list)
        self.client.execute_query()

    def test3_create_folder_in_list(self):
        new_folder = self.target_list.rootFolder.add("Archive")
        self.client.execute_query()
        self.assertIsNotNone(new_folder.serverRelativeUrl)

    def test4_get_list_item(self):
        item = self.target_list.get_item_by_id(self.__class__.target_item.properties["Id"])
        self.client.load(item)
        self.client.execute_query()
        self.assertIsNotNone(item.properties["Id"])

    def test5_get_list_item_via_caml(self):
        item_id = self.__class__.target_item.properties["Id"]
        caml_query = CamlQuery.parse(
            "<Where><Eq><FieldRef Name='ID' /><Value Type='Counter'>{0}</Value></Eq></Where>".format(item_id))
        result = self.target_list.get_items(caml_query)
        self.client.execute_query()
        self.assertEqual(len(result), 1)

    def test6_update_listItem(self):
        item_to_update = self.__class__.target_item
        self.client.load(item_to_update)
        self.client.execute_query()
        last_updated = item_to_update.properties['Modified']

        sleep(1)
        new_title = "Task item %s" % random_seed
        item_to_update.set_property('Title', new_title)
        item_to_update.update()
        self.client.load(item_to_update)  # retrieve updated
        self.client.execute_query()
        self.assertNotEqual(item_to_update.properties["Modified"], last_updated)
        self.assertNotEqual(self.default_title, new_title)

    def test7_systemUpdate_listItem(self):
        item_to_update = self.__class__.target_item
        self.client.load(item_to_update)
        self.client.execute_query()
        last_updated = item_to_update.properties['Modified']

        new_title = "Task item %s" % random_seed
        item_to_update.set_property('Title', new_title)
        item_to_update.system_update()
        self.client.load(item_to_update)  # retrieve updated
        self.client.execute_query()
        self.assertEqual(item_to_update.properties["Modified"], last_updated)
        self.assertNotEqual(self.default_title, new_title)

    def test8_update_overwrite_version(self):
        item_to_update = self.__class__.target_item
        item_to_update.update_overwrite_version()
        self.client.execute_query()

    def test9_delete_list_item(self):
        item_id = self.__class__.target_item.properties["Id"]
        item_to_delete = self.__class__.target_item
        item_to_delete.delete_object()
        self.client.execute_query()

        result = self.target_list.items.filter("Id eq {0}".format(item_id))
        self.client.load(result)
        self.client.execute_query()
        self.assertEqual(0, len(result))

    def test_10_create_multiple_items(self):
        for i in range(0, self.batch_items_count):
            item_properties = {'Title': "Task {0}".format(i)}
            self.target_list.add_item(item_properties)
        self.client.execute_batch()
        result = self.target_list.items.get().execute_query()
        self.assertEqual(len(result), self.batch_items_count)

    def test_11_delete_multiple_items(self):
        result = self.target_list.items.get().execute_query()  # get existing items
        self.assertGreater(len(result), 0)
        for item in result:
            item.delete_object()
        self.client.execute_batch()
        result_after = self.target_list.items.get().execute_query()
        self.assertEqual(len(result_after), 0)
