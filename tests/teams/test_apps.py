import uuid

from tests.graph_case import GraphTestCase

from office365.teams.team import Team


class TestTeamApps(GraphTestCase):
    """Tests for team Apps"""

    target_team = None  # type: Team

    @classmethod
    def setUpClass(cls):
        super(TestTeamApps, cls).setUpClass()
        team_name = "Team_" + uuid.uuid4().hex
        result = cls.client.teams.create(team_name)
        cls.client.execute_query_retry()
        cls.target_team = result.value

    @classmethod
    def tearDownClass(cls):
        group_id = cls.target_team.id
        cls.client.groups[group_id].delete_object().execute_query()

    def test1_get_team_apps(self):
        apps = self.__class__.target_team.installed_apps.get().execute_query()
        self.assertIsNotNone(apps.resource_path)
