from tests.graph_case import GraphTestCase


class TestSecurityReports(GraphTestCase):
    @classmethod
    def setUpClass(cls):
        super(TestSecurityReports, cls).setUpClass()

    @classmethod
    def tearDownClass(cls):
        pass

    def test1_get_attack_simulation_repeat_offenders(self):
        result = (
            self.client.reports.security.get_attack_simulation_repeat_offenders().execute_query()
        )
        self.assertIsNotNone(result.value)
