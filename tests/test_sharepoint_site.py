from tests.sharepoint_case import SPTestCase


class TestSite(SPTestCase):
    def test_if_site_loaded(self):
        site = self.context.site
        self.context.load(site)
        self.context.execute_query()
        self.assertIs(site.is_property_available('Url'), True, "Site resource was not requested")
        self.assertIs(site.is_property_available('RootWeb'), False)
