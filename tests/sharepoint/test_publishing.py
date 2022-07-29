from office365.sharepoint.publishing.pages.collection import SitePageCollection
from office365.sharepoint.publishing.pages.service import SitePageService
from office365.sharepoint.publishing.primary_city_time import PrimaryCityTime
from office365.sharepoint.publishing.pages.page import SitePage
from office365.sharepoint.publishing.video.service_discoverer import VideoServiceDiscoverer
from tests.sharepoint.sharepoint_case import SPTestCase


class TestSPPublishing(SPTestCase):

    @classmethod
    def setUpClass(cls):
        super(TestSPPublishing, cls).setUpClass()

    @classmethod
    def tearDownClass(cls):
        pass

    def test1_init_site_page_service(self):
        svc = SitePageService(self.client).get().execute_query()
        self.assertIsNotNone(svc.resource_path)

    def test2_get_site_pages(self):
        svc = SitePageService(self.client)
        pages = svc.pages.get().execute_query()
        self.assertIsInstance(pages, SitePageCollection)

    def test3_get_time_zone(self):
        time_zone = SitePageService.get_time_zone(self.client, "Moscow").execute_query()
        self.assertIsInstance(time_zone, PrimaryCityTime)
        # self.assertEqual(time_zone.properties.get("Location"), "Moscow, Russia")

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
        self.assertIsNotNone(discoverer.resource_path)

    def test8_get_page_translations(self):
        pages = self.client.site_pages.pages.get().filter("FileName eq 'Home.aspx'").execute_query()
        self.assertEqual(len(pages), 1)
        first_page = pages[0]  # type: SitePage

        #translations = first_page.translations.get().execute_query()
        #self.assertIsNotNone(translations.resource_path)

    def test9_can_create_page(self):
        result = self.client.site_pages.can_create_page().execute_query()
        self.assertIsNotNone(result.value)

