from office365.sharepoint.navigation.navigation_node import NavigationNode
from office365.sharepoint.navigation.navigation_node_collection import NavigationNodeCollection
from office365.sharepoint.navigation.navigation_node_creation_information import NavigationNodeCreationInformation
from office365.sharepoint.navigation.navigation_service import NavigationService
from tests.sharepoint.sharepoint_case import SPTestCase


class TestNavigation(SPTestCase):
    target_node = None  # type: NavigationNode

    @classmethod
    def setUpClass(cls):
        super(TestNavigation, cls).setUpClass()
        cls.nav_svc = NavigationService(cls.client)

    def test_2_is_global_nav_enabled(self):
        # self.nav_svc.set_global_nav_enabled(True).execute_query()
        result = self.nav_svc.global_nav_enabled()
        self.nav_svc.execute_query()
        self.assertIsNotNone(result.value)

    def test_3_get_web_navigation(self):
        web_nav = self.client.web.navigation.expand(["TopNavigationBar"]).get().execute_query()
        self.assertIsNotNone(web_nav.resource_path)
        self.assertIsInstance(web_nav.top_navigation_bar, NavigationNodeCollection)

    def test_4_create_navigation_node(self):
        node_create_info = NavigationNodeCreationInformation("Technical documentation",
                                                             "https://docs.microsoft.com/en-us/documentation/", True)
        new_node = self.client.web.navigation.quick_launch.add(node_create_info).execute_query()
        self.assertIsNotNone(new_node.resource_path)
        self.__class__.target_node = new_node

    def test_5_get_navigation_node_by_id(self):
        node_id = self.__class__.target_node.properties.get('Id')
        existing_node = self.client.web.navigation.quick_launch.get_by_id(node_id).get().execute_query()
        self.assertIsNotNone(existing_node.resource_path)

    def test_6_get_navigation_node_by_index(self):
        existing_node = self.client.web.navigation.quick_launch.get_by_index(0).get().execute_query()
        self.assertIsNotNone(existing_node.resource_path)

    def test_7_delete_navigation_node(self):
        node_to_del = self.__class__.target_node
        node_to_del.delete_object().execute_query()


    # def test1_ensure_home_site(self):
    #    result = self.client.site.is_valid_home_site()
    #    self.client.execute_query()
    #    self.assertIsInstance(result.value, bool)
    #    if result.value is False:
    #        result = self.client.site.set_as_home_site()
    #        self.client.execute_query()
    #        self.assertIsNotNone(result.value)

    # def test2_get_publishing_navigation_provider_type(self):
    #    result = self.nav_svc.get_publishing_navigation_provider_type()
    #    self.client.execute_query()
    #    self.assertIsInstance(result.value, int)

    # def test3_global_nav(self):
    #    result = self.nav_svc.global_nav()
    #    self.client.execute_query()
    #    self.assertIsNotNone(result)
