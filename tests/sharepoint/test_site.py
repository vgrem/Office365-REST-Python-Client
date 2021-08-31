from tests.sharepoint.sharepoint_case import SPTestCase

from office365.sharepoint.lists.list_template_type import ListTemplateType
from office365.sharepoint.sites.site import Site


class TestSite(SPTestCase):
    target_site = None  # type: Site

    def test1_if_site_loaded(self):
        site = self.client.site.get().execute_query()
        self.assertIs(site.is_property_available('Url'), True, "Site resource was not requested")
        self.assertIs(site.is_property_available('RootWeb'), False)
        self.__class__.target_site = site

    def test2_if_site_exists(self):
        site_url = self.__class__.target_site.url
        result = Site.exists(self.client, site_url).execute_query()
        self.assertIsNotNone(result.value)

    def test3_get_site_by_id(self):
        site_id = self.__class__.target_site.properties['Id']
        result = Site.get_url_by_id(self.client, site_id).execute_query()
        self.assertIsNotNone(result.value)

    def test4_get_site_catalog(self):
        catalog = self.client.site.get_catalog(ListTemplateType.AppDataCatalog).get().execute_query()
        self.assertIsNotNone(catalog.title)

    def test5_get_web_templates(self):
        web_templates = self.client.site.get_web_templates().execute_query()
        self.assertIsNotNone(web_templates)

    def test6_get_web_template_by_name(self):
        template_name = "GLOBAL#0"
        web_template = self.client.site.get_web_templates().get_by_name(template_name).get().execute_query()
        self.assertIsNotNone(web_template)

    def test7_get_site_logo(self):
        result = self.client.site.get_site_logo().execute_query()
        self.assertIsNotNone(result.value)

