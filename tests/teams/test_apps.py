import uuid

from tests.graph_case import GraphTestCase


class TestTeamApps(GraphTestCase):
    """Tests for team Apps"""

    target_team = None  # type: Team

    @classmethod
    def setUpClass(cls):
        super(TestTeamApps, cls).setUpClass()
        team_name = "Team_" + uuid.uuid4().hex
        new_team = cls.client.teams.create(team_name).get().execute_query_retry()
        cls.target_team = new_team

    @classmethod
    def tearDownClass(cls):
        cls.target_team.delete_object().execute_query_retry()

    def test1_get_team_apps(self):
        apps = self.__class__.target_team.installed_apps.get().execute_query()
        self.assertIsNotNone(apps.resource_path)
