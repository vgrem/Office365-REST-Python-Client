from tests.sharepoint_case import SPTestCase


class TestSite(SPTestCase):

    def test1_if_site_loaded(self):
        site = self.client.site
        self.client.load(site)
        self.client.execute_query()
        self.assertIs(site.is_property_available('Url'), True, "Site resource was not requested")
        self.assertIs(site.is_property_available('RootWeb'), False)
