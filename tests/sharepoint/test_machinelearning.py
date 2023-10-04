from tests.sharepoint.sharepoint_case import SPTestCase


class TestMachineLearningHub(SPTestCase):
    def test1_enabled(self):
        result = (
            self.client.machine_learning.machine_learning_enabled.get().execute_query()
        )
        self.assertIsNotNone(result)

    def test2_get_default_content_center_site(self):
        # from office365.sharepoint.client_context import ClientContext
        # from tests import test_admin_site_url
        # from tests import test_admin_credentials
        # admin_client = ClientContext(test_admin_site_url).with_credentials(test_admin_credentials)
        # tenant = admin_client.tenant.select(["DefaultContentCenterSite"]).get().execute_query()
        # self.assertIsNotNone(tenant.default_content_center_site)
        pass
