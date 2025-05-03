from office365.sharepoint.publishing.pages.page import SitePage
from tests.sharepoint.sharepoint_case import SPTestCase


class TestMultilingual(SPTestCase):
    """"""

    site_page = None  # type: SitePage

    def test1_is_web_multilingual(self):
        web = (
            self.client.web.select(["IsMultilingual", "SupportedUILanguageIds"])
            .expand(["MultilingualSettings"])
            .get()
            .execute_query()
        )
        self.assertIsNotNone(web.is_multilingual)
        self.assertIsNotNone(web.supported_ui_language_ids)
        self.assertIsNotNone(web.multilingual_settings)

    def test2_create_page(self):
        page_title = "My Page"
        site_page = self.client.site_pages.create_page(
            page_title, language="en-us"
        ).execute_query()
        self.assertIsNotNone(site_page.resource_path)
        self.__class__.site_page = site_page

    def test3_get_page_language(self):
        site_page = self.__class__.site_page.get().select(["Language"]).execute_query()
        self.assertIsNotNone(site_page.language)
