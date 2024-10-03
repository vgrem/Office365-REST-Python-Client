from tests import test_team_site_url
from tests.graph_case import GraphTestCase


class TestSitePage(GraphTestCase):
    """OneDrive specific test case base class"""

    @classmethod
    def setUpClass(cls):
        super(TestSitePage, cls).setUpClass()
        cls.test_site = cls.client.sites.get_by_url(test_team_site_url)

    @classmethod
    def tearDownClass(cls):
        pass

    def test1_list_site_pages(self):
        result = self.test_site.pages.top(10).get().execute_query()
        self.assertIsNotNone(result.resource_path)

    # def test2_get_site_page_by_name(self):
    #    result = self.test_site.pages.get_by_name("Home.aspx").execute_query()
    #    self.assertIsNotNone(result.resource_path)
