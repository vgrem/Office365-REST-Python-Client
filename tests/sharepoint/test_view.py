from tests import random_seed
from tests.sharepoint.sharepoint_case import SPTestCase

from office365.sharepoint.changes.change_query import ChangeQuery
from office365.sharepoint.lists.list import List
from office365.sharepoint.lists.list_creation_information import ListCreationInformation
from office365.sharepoint.lists.list_template_type import ListTemplateType
from office365.sharepoint.views.view import View
from office365.sharepoint.views.view_create_information import ViewCreationInformation


class TestSPView(SPTestCase):
    target_list = None  # type: List
    target_view = None  # type: View

    @classmethod
    def setUpClass(cls):
        super(TestSPView, cls).setUpClass()
        cls.target_list = cls.ensure_list(cls.client.web,
                                          ListCreationInformation("Tasks",
                                                                  None,
                                                                  ListTemplateType.Tasks)
                                          )

    @classmethod
    def tearDownClass(cls):
        cls.target_list.delete_object().execute_query()

    def test1_get_all_views(self):
        all_views = self.target_list.views.get().execute_query()
        self.assertGreater(len(all_views), 1)

    def test2_create_view(self):
        view_properties = ViewCreationInformation()
        view_properties.Title = "My Tasks %s" % random_seed
        view_properties.PersonalView = True
        view_properties.Query = "<Where><Eq><FieldRef ID='AssignedTo' /><Value " \
                                "Type='Integer'><UserID/></Value></Eq></Where> "

        new_view = self.target_list.views.add(view_properties).execute_query()
        self.assertEqual(view_properties.Title, new_view.properties['Title'])
        self.__class__.target_view = new_view

    def test3_read_view(self):
        view_to_read = self.__class__.target_view.get().execute_query()
        self.assertIsNotNone(view_to_read.resource_path)

    def test4_get_default_view_items(self):
        view_items = self.target_list.defaultView.get_items().get().execute_query()
        self.assertIsNotNone(view_items.resource_path)

    def test5_get_view_items(self):
        view_items = self.__class__.target_view.get_items().get().execute_query()
        self.assertIsNotNone(view_items.resource_path)

    def test6_update_view(self):
        target_view_title_updated = self.__class__.target_view.properties["Title"] + "_updated"
        view_to_update = self.__class__.target_view
        view_to_update.set_property('Title', target_view_title_updated)
        view_to_update.update().execute_query().execute_query()

        result = self.target_list.views.filter("Title eq '{0}'".format(target_view_title_updated)).get().execute_query()
        self.assertEqual(len(result), 1)

    def test7_get_view_changes(self):
        changes = self.client.site.get_changes(ChangeQuery(view=True)).execute_query()
        self.assertGreater(len(changes), 0)

    def test8_delete_view(self):
        view_to_delete = self.__class__.target_view
        view_to_delete.delete_object().execute_query()
