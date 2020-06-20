from office365.sharepoint.lists.list_template_type import ListTemplateType
from office365.sharepoint.sites.site import Site
from tests.sharepoint.sharepoint_case import SPTestCase


class TestSite(SPTestCase):

    target_site = None  # type: Site

    def test1_if_site_loaded(self):
        site = self.client.site
        self.client.load(site)
        self.client.execute_query()
        self.assertIs(site.is_property_available('Url'), True, "Site resource was not requested")
        self.assertIs(site.is_property_available('RootWeb'), False)
        self.__class__.target_site = site

    def test2_if_site_exists(self):
        site_url = self.__class__.target_site.properties['Url']
        result = Site.exists(self.client, site_url)
        self.client.execute_query()
        self.assertIsNotNone(result.value)

    def test3_get_site_by_id(self):
        site_id = self.__class__.target_site.properties['Id']
        result = Site.get_url_by_id(self.client, site_id)
        self.client.execute_query()
        self.assertIsNotNone(result.value)

    def test4_get_site_catalog(self):
        catalog = self.client.site.get_catalog(ListTemplateType.AppDataCatalog)
        self.client.load(catalog)
        self.client.execute_query()
        self.assertIsNotNone(catalog)
