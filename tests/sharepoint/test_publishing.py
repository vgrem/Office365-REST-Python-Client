from office365.sharepoint.publishing.pages.collection import SitePageCollection
from office365.sharepoint.publishing.pages.service import SitePageService
from office365.sharepoint.publishing.video.service_discoverer import VideoServiceDiscoverer
from tests.sharepoint.sharepoint_case import SPTestCase


class TestPublishing(SPTestCase):

    @classmethod
    def setUpClass(cls):
        super(TestPublishing, cls).setUpClass()

    @classmethod
    def tearDownClass(cls):
        pass

    def test1_init_site_page_service(self):
        svc = self.client.site_pages.get().execute_query()
        self.assertIsNotNone(svc.resource_path)

    def test2_list_site_pages(self):
        pages = self.client.site_pages.pages.get().execute_query()
        self.assertIsInstance(pages, SitePageCollection)

    # def test3_get_time_zone(self):
    #    time_zone = SitePageService.get_time_zone(self.client, "Moscow").execute_query()
    #    self.assertIsInstance(time_zone, PrimaryCityTime)

    def test4_compute_file_name(self):
        result = SitePageService.compute_file_name(self.client, "Test page").execute_query()
        self.assertIsNotNone(result.value)

    def test5_file_picker_tab_options(self):
        result = SitePageService.file_picker_tab_options(self.client).execute_query()
        self.assertIsNotNone(result.value)

    def test6_org_assets(self):
        result = SitePageService.org_assets(self.client).execute_query()
        self.assertIsNotNone(result.value)

    def test7_get_video_service_manager(self):
        discoverer = VideoServiceDiscoverer(self.client).get().execute_query()
        self.assertIsNotNone(discoverer.video_portal_url)

    def test8_get_page_by_name(self):
        page = self.client.site_pages.pages.get_by_name("Home.aspx").get().execute_query()
        self.assertIsNotNone(page.resource_path)

    def test9_can_create_page(self):
        result = self.client.site_pages.can_create_page().execute_query()
        self.assertIsNotNone(result.value)

    def test_10_get_current_user_memberships(self):
        result = SitePageService.get_current_user_memberships(self.client).execute_query()
        self.assertIsNotNone(result.value)

    def test_11_get_page_diagnostics(self):
        result = self.client.page_diagnostics.by_page("/sites/team/SitePages/Home.aspx").execute_query()
        self.assertIsNotNone(result.value)

    #def test_12_share_page_preview_by_email(self):
    #    page = self.client.site_pages.pages.get_by_url("/sites/team/SitePages/Home.aspx")
    #    page.share_page_preview_by_email("This page has been shared with you",
    #                                     [test_user_principal_name_alt]).execute_query()
