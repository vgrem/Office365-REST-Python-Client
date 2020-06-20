from office365.sharepoint.lists.list import List
from office365.sharepoint.lists.list_creation_information import ListCreationInformation
from office365.sharepoint.lists.list_template_type import ListTemplateType
from office365.sharepoint.views.view_create_information import ViewCreationInformation
from tests import random_seed
from tests.sharepoint.sharepoint_case import SPTestCase


class TestSPView(SPTestCase):
    target_list = None  # type: List

    @classmethod
    def setUpClass(cls):
        super(TestSPView, cls).setUpClass()
        cls.target_list = cls.ensure_list(cls.client.web,
                                          ListCreationInformation("Tasks",
                                                                  None,
                                                                  ListTemplateType.Tasks)
                                          )
        cls.target_view_title = "My Tasks %s" % random_seed
        cls.target_view_title_updated = cls.target_view_title + "_updated"

    @classmethod
    def tearDownClass(cls):
        cls.target_list.delete_object()
        cls.client.execute_query()

    def test1_get_all_views(self):
        all_views = self.target_list.views
        self.client.load(all_views)
        self.client.execute_query()
        for cur_view in all_views:
            self.assertIsNotNone(cur_view.resource_path)

    def test2_create_view(self):
        view_properties = ViewCreationInformation()
        view_properties.Title = self.target_view_title
        view_properties.PersonalView = True
        view_properties.Query = "<Where><Eq><FieldRef ID='AssignedTo' /><Value " \
                                "Type='Integer'><UserID/></Value></Eq></Where> "

        view_to_create = self.target_list.views.add(view_properties)
        self.client.execute_query()
        self.assertEqual(view_properties.Title, view_to_create.properties['Title'])

    def test3_read_view(self):
        view_to_read = self.target_list.views.get_by_title(self.target_view_title)
        self.client.load(view_to_read)
        self.client.execute_query()
        self.assertEqual(self.target_view_title, view_to_read.properties['Title'])

    def test4_get_default_view_items(self):
        view_items = self.target_list.defaultView.get_items()
        self.client.load(view_items)
        self.client.execute_query()
        self.assertIsNotNone(view_items.resource_path)

    def test5_get_view_items(self):
        view_items = self.target_list.views.get_by_title(self.target_view_title).get_items()
        self.client.load(view_items)
        self.client.execute_query()
        self.assertIsNotNone(view_items.resource_path)

    def test6_update_view(self):
        view_to_update = self.target_list.views.get_by_title(self.target_view_title)
        view_to_update.set_property('Title', self.target_view_title_updated)
        view_to_update.update()
        self.client.execute_query()

        result = self.target_list.views.filter("Title eq '{0}'".format(self.target_view_title_updated))
        self.client.load(result)
        self.client.execute_query()
        self.assertEqual(len(result), 1)

    def test7_delete_view(self):
        view_to_delete = self.target_list.views.get_by_title(self.target_view_title_updated)
        view_to_delete.delete_object()
        self.client.execute_query()

        result = self.client.web.lists.filter("Title eq '{0}'".format(self.target_view_title_updated))
        self.client.load(result)
        self.client.execute_query()
        self.assertEqual(len(result), 0)
