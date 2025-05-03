from tests.graph_case import GraphTestCase


class TestAdmin(GraphTestCase):
    """SharePoint specific test case base class"""

    def test1_get_sharepoint_settings(self):
        result = self.client.admin.sharepoint.settings.get().execute_query()
        self.assertIsNotNone(result.resource_path)

    def test2_update_sharepoint_settings(self):
        settings = self.client.admin.sharepoint.settings
        settings.sharing_blocked_domain_list = ["contoso.com", "fabrikam.com"]
        settings.update().execute_query()

    def test3_list_issues(self):
        result = self.client.admin.service_announcement.issues.get().execute_query()
        self.assertIsNotNone(result.resource_path)

    def test4_list_microsoft365_apps(self):
        result = self.client.admin.microsoft365_apps.get().execute_query()
        self.assertIsNotNone(result.resource_path)

    # def test5_get_admin_people(self):
    #    result = self.client.admin.people.get().execute_query()
    #    self.assertIsNotNone(result.resource_path)
