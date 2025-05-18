from office365.onedrive.sitepages.site_page import SitePage
from tests import create_unique_name, test_team_site_url
from tests.graph_case import GraphTestCase


class TestWebPart(GraphTestCase):
    """OneDrive specific test case for web parts"""

    target_page = None  # type: SitePage

    @classmethod
    def setUpClass(cls):
        super(TestWebPart, cls).setUpClass()
        test_site = cls.client.sites.get_by_url(test_team_site_url)
        page_name = create_unique_name("Test Page")
        cls.target_page = test_site.pages.add(page_name).checkin("").execute_query()

    @classmethod
    def tearDownClass(cls):
        cls.target_page.delete_object().execute_query()

    def test1_list_web_parts(self):
        result = self.target_page.web_parts.get().execute_query()
        self.assertIsNotNone(result.resource_path)
