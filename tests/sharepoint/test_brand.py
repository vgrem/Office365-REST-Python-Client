from tests.sharepoint.sharepoint_case import SPTestCase


class TestBrand(SPTestCase):

    def test1_get_site_themes(self):
        result = self.client.brand_center.get_site_themes().execute_query()
        self.assertIsNotNone(result.value)

    def test2_get_configuration(self):
        result = self.client.brand_center.configuration().execute_query()
        self.assertIsNotNone(result.value)
