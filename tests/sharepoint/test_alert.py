from tests.sharepoint.sharepoint_case import SPTestCase


class TestAlert(SPTestCase):
    def test_1_get_web_alerts(self):
        alerts = self.client.web.alerts.get().execute_query()
        self.assertIsNotNone(alerts.resource_path)

    def test_2_get_user_alerts(self):
        alerts = self.client.web.current_user.alerts.get().execute_query()
        self.assertIsNotNone(alerts.resource_path)
