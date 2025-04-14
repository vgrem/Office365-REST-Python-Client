from tests.graph_case import GraphTestCase


class TestTeamsReports(GraphTestCase):
    @classmethod
    def setUpClass(cls):
        super(TestTeamsReports, cls).setUpClass()

    @classmethod
    def tearDownClass(cls):
        pass

    def test1_get_teams_team_counts(self):
        result = self.client.reports.get_teams_team_counts("D90").execute_query()
        self.assertIsNotNone(result.value)
