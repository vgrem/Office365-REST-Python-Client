from tests.graph_case import GraphTestCase


class TestIntuneReports(GraphTestCase):
    @classmethod
    def setUpClass(cls):
        super(TestIntuneReports, cls).setUpClass()

    @classmethod
    def tearDownClass(cls):
        pass

    def test1_device_configuration_user_activity(self):
        result = (
            self.client.reports.device_configuration_user_activity().execute_query()
        )
        self.assertIsNotNone(result.value)
