from tests.graph_case import GraphTestCase


class TestSitePage(GraphTestCase):
    """OneDrive specific test case base class"""

    @classmethod
    def setUpClass(cls):
        super(TestSitePage, cls).setUpClass()
        cls.test_site = cls.client.sites.root

    @classmethod
    def tearDownClass(cls):
        pass

    def test1_list_site_pages(self):
        result = self.test_site.pages.get().execute_query()
        self.assertIsNotNone(result.resource_path)
