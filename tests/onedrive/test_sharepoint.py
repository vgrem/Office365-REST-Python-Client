from tests.graph_case import GraphTestCase


class TestSharePoint(GraphTestCase):
    """SharePoint specific test case base class"""

    def test1_get_sharepoint_settings(self):
        result = self.client.admin.sharepoint.settings.get().execute_query()
        self.assertIsNotNone(result.resource_path)

    def test2_list_issues(self):
        result = self.client.admin.service_announcement.issues.get().execute_query()
        self.assertIsNotNone(result.resource_path)
