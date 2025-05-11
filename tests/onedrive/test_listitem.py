from office365.onedrive.listitems.list_item import ListItem
from office365.onedrive.lists.list import List
from tests import test_team_site_url
from tests.graph_case import GraphTestCase


class TestListItem(GraphTestCase):
    """"""

    target_list = None  # type: List
    target_item = None  # type: ListItem

    @classmethod
    def setUpClass(cls):
        super(TestListItem, cls).setUpClass()
        cls.test_site = cls.client.sites.get_by_url(test_team_site_url)
        cls.pages_list = cls.test_site.lists.get_by_name("Site Pages")

    @classmethod
    def tearDownClass(cls):
        pass

    def test_1_get_item_by_name(self):
        result = self.pages_list.items.get_by_name("Home.aspx").execute_query()
        self.assertIsNotNone(result.resource_path)
        self.__class__.target_item = result

    def test_3_get_item_values(self):
        item = self.__class__.target_item
        result = item.fields.get().execute_query()
        self.assertIsNotNone(result.resource_path)
