from office365.onedrive.lists.list import List
from tests.graph_case import GraphTestCase


class TestList(GraphTestCase):
    """OneDrive specific test case base class"""
    target_list = None  # type: List

    @classmethod
    def setUpClass(cls):
        super(TestList, cls).setUpClass()

    @classmethod
    def tearDownClass(cls):
        pass

    def test1_get_list(self):
        target_list = self.client.sites.root.lists["Documents"].get().execute_query()
        self.assertIsNotNone(target_list.resource_path)
        self.__class__.target_list = target_list

    def test2_get_list_items(self):
        items = self.target_list.items.get().execute_query()
        self.assertIsNotNone(items.resource_path)

    def test3_get_list_columns(self):
        columns = self.target_list.columns.get().execute_query()
        self.assertIsNotNone(columns.resource_path)

