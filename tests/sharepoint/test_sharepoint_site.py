from office365.sharepoint.list_template_type import ListTemplateType
from office365.sharepoint.site import Site
from tests.sharepoint.sharepoint_case import SPTestCase


class TestSite(SPTestCase):

    def test1_if_site_loaded(self):
        site = self.client.site
        self.client.load(site)
        self.client.execute_query()
        self.assertIs(site.is_property_available('Url'), True, "Site resource was not requested")
        self.assertIs(site.is_property_available('RootWeb'), False)

    def test2_if_site_exists(self):
        result = Site.exists(self.client, "https://mediadev8.sharepoint.com/sites/team")
        self.client.execute_query()
        self.assertIsNotNone(result.value)

    def test3_get_site_catalog(self):
        catalog = self.client.site.get_catalog(ListTemplateType.AppDataCatalog)
        self.client.load(catalog)
        self.client.execute_query()
        self.assertIsNotNone(catalog)
