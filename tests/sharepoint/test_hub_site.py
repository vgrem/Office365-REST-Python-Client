from office365.sharepoint.portal.hub_sites_utility import SPHubSitesUtility
from tests.sharepoint.sharepoint_case import SPTestCase


class TestHubSite(SPTestCase):

    @classmethod
    def setUpClass(cls):
        super(TestHubSite, cls).setUpClass()
        cls.target_site = cls.client.site.get().execute_query()

    def test1_register_hub_site(self):
        if not self.target_site.is_hub_site:
            site = self.target_site.register_hub_site(None).get().execute_query()
            self.assertTrue(site.is_hub_site)

    def test2_get_hub_sites(self):
        hub_sites = SPHubSitesUtility(self.client).get_hub_sites().execute_query()
        self.assertGreater(len(hub_sites), 0)

    def test3_unregister_hub_site(self):
        site = self.target_site.unregister_hub_site().get().execute_query()
        self.assertFalse(site.is_hub_site)

