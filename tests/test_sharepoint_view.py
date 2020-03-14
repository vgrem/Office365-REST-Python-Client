from office365.sharepoint.list_creation_information import ListCreationInformation
from office365.sharepoint.list_template_type import ListTemplateType
from office365.sharepoint.view_create_information import ViewCreationInformation
from tests import random_seed
from tests.sharepoint_case import SPTestCase
from tests.test_methods import ensure_list


class TestSPView(SPTestCase):

    target_list = None

    @classmethod
    def setUpClass(cls):
        super(TestSPView, cls).setUpClass()
        cls.target_list = ensure_list(cls.client.web,
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

    def test1_create_view(self):
        view_properties = ViewCreationInformation()
        view_properties.Title = self.target_view_title
        view_properties.PersonalView = True
        view_properties.Query = "<Where><Eq><FieldRef ID='Assigned To' /><Value " \
                                "Type='Integer'><UserID/></Value></Eq></Where> "

        view_to_create = self.target_list.views.add(view_properties)
        self.client.execute_query()
        self.assertEqual(view_properties.Title, view_to_create.properties['Title'])

    def test2_read_view(self):
        view_to_read = self.target_list.views.get_by_title(self.target_view_title)
        self.client.load(view_to_read)
        self.client.execute_query()
        self.assertEqual(self.target_view_title, view_to_read.properties['Title'])

    def test4_update_view(self):
        view_to_update = self.target_list.views.get_by_title(self.target_view_title)
        view_to_update.set_property('Title', self.target_view_title_updated)
        view_to_update.update()
        self.client.execute_query()

        result = self.target_list.views.filter("Title eq '{0}'".format(self.target_view_title_updated))
        self.client.load(result)
        self.client.execute_query()
        self.assertEqual(len(result), 1)

    def test5_delete_view(self):
        view_to_delete = self.target_list.views.get_by_title(self.target_view_title_updated)
        view_to_delete.delete_object()
        self.client.execute_query()

        result = self.client.web.lists.filter("Title eq '{0}'".format(self.target_view_title_updated))
        self.client.load(result)
        self.client.execute_query()
        self.assertEqual(len(result), 0)
