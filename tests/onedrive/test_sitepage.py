from office365.onedrive.sitepages.site_page import SitePage
from tests import create_unique_name, test_team_site_url
from tests.graph_case import GraphTestCase


class TestSitePage(GraphTestCase):
    """OneDrive specific test case base class"""

    target_page = None  # type: SitePage

    @classmethod
    def setUpClass(cls):
        super(TestSitePage, cls).setUpClass()
        cls.test_site = cls.client.sites.get_by_url(test_team_site_url)
        cls.page_name = create_unique_name("Test Page")

    @classmethod
    def tearDownClass(cls):
        pass

    def test1_create_site_page(self):
        result = self.test_site.pages.add(self.page_name).execute_query()
        self.assertIsNotNone(result.resource_path)
        self.__class__.target_page = result

    def test2_get_site_page(self):
        page = self.__class__.target_page
        result = page.get().execute_query()
        self.assertIsNotNone(result.resource_path)

    def test3_checkin_site_page(self):
        page = self.__class__.target_page
        result = page.checkin("Initial version").execute_query()
        self.assertIsNotNone(result.resource_path)

    def test4_get_site_page_pub_state(self):
        page = self.__class__.target_page
        result = page.get().select(["publishingState"]).execute_query()
        self.assertIsNotNone(result.publishing_state.level)

    # def test5_publish_site_page(self):
    #    page = self.__class__.target_page
    #    result = page.publish().execute_query()
    #    self.assertIsNotNone(result.resource_path)

    def test6_list_site_pages(self):
        result = self.test_site.pages.top(10).get().execute_query()
        self.assertIsNotNone(result.resource_path)

    # def test7_get_site_page_by_name(self):
    #    result = self.test_site.pages.get_by_name(self.page_name).execute_query()
    #    self.assertIsNotNone(result.resource_path)

    # def test8_get_site_page_by_title(self):
    #    page = self.__class__.target_page
    #    result = self.test_site.pages.get_by_title(page.title).execute_query()
    #    self.assertIsNotNone(result.resource_path)

    # def test9_get_web_parts_by_position(self):
    #    page = self.__class__.target_page
    #    result = page.get_web_parts_by_position().execute_query()
    #    self.assertIsNotNone(result.resource_path)

    def test_10_delete_site_page(self):
        page = self.__class__.target_page
        page.delete_object().execute_query()

    def test_11_get_site_page_list(self):
        result = self.test_site.lists.get_by_name("Site Pages").get().execute_query()
        self.assertIsNotNone(result.resource_path)
