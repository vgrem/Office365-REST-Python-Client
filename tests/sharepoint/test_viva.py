from tests.sharepoint.sharepoint_case import SPTestCase


class TestViva(SPTestCase):
    def test1_get_app_configuration(self):
        return_type = self.client.ee.app_configuration.get().execute_query()
        self.assertIsNotNone(return_type.resource_path)

    # def test2_get_viva_home(self):
    #    return_type = self.client.ee.viva_home().execute_query()
    #    self.assertIsNotNone(return_type.resource_path)

    # def test2_get_dashboard_content(self):
    #    return_type = self.client.ee.dashboard_content().execute_query()
    #    self.assertIsNotNone(return_type.value)
