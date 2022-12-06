from tests.sharepoint.sharepoint_case import SPTestCase


class TestOrgNews(SPTestCase):

    def test_1_get_org_news(self):
        result = self.client.org_news.get().execute_query()
        self.assertIsNotNone(result.resource_path)

    def test2_sites_reference(self):
        result = self.client.org_news.sites_reference().execute_query()
        self.assertIsNotNone(result.value)
