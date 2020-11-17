from office365.sharepoint.navigation.navigationService import NavigationService
from tests.sharepoint.sharepoint_case import SPTestCase


class TestNavigation(SPTestCase):

    @classmethod
    def setUpClass(cls):
        super(TestNavigation, cls).setUpClass()
        cls.nav_svc = NavigationService(cls.client)

    #def test1_ensure_home_site(self):
    #    result = self.client.site.is_valid_home_site()
    #    self.client.execute_query()
    #    self.assertIsInstance(result.value, bool)
    #    if result.value is False:
    #        result = self.client.site.set_as_home_site()
    #        self.client.execute_query()
    #        self.assertIsNotNone(result.value)

    #def test2_get_publishing_navigation_provider_type(self):
    #    result = self.nav_svc.get_publishing_navigation_provider_type()
    #    self.client.execute_query()
    #    self.assertIsInstance(result.value, int)

    #def test3_global_nav(self):
    #    result = self.nav_svc.global_nav()
    #    self.client.execute_query()
    #    self.assertIsNotNone(result)
