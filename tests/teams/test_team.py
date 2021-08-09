import uuid

from office365.teams.team import Team
from tests.graph_case import GraphTestCase


class TestGraphTeam(GraphTestCase):
    """Tests for teams"""

    target_team = None  # type: Team

    @classmethod
    def setUpClass(cls):
        super(TestGraphTeam, cls).setUpClass()

    def test1_create_team_from_group(self):
        grp_name = "Group_" + uuid.uuid4().hex
        result = self.client.teams.create(grp_name).execute_query_retry(max_retry=6, timeout_secs=5)
        self.assertIsNotNone(result.value.id)
        self.__class__.target_team = result.value

    def test3_get_all_teams(self):
        teams = self.client.teams.get_all().execute_query()
        self.assertGreater(len(teams), 0)

    def test4_get_joined_teams(self):
        my_teams = self.client.me.joined_teams.get().execute_query()
        self.assertIsNotNone(my_teams.resource_path)
        self.assertGreater(len(my_teams), 0)

    def test5_get_team(self):
        group_id = self.__class__.target_team.id
        existing_team = self.client.teams[group_id].get().execute_query()
        self.assertIsNotNone(existing_team.resource_url)
        self.assertIsNotNone(existing_team.messaging_settings)

        if existing_team.is_archived:
            existing_team.unarchive()
            self.client.load(existing_team)
            self.client.execute_query()
            self.assertFalse(existing_team.is_archived)

    def test6_update_team(self):
        team_id = self.__class__.target_team.id
        team_to_update = self.client.teams[team_id]
        team_to_update.fun_settings.allowGiphy = False
        team_to_update.update().execute_query()

    def test7_archive_team(self):
        team_id = self.__class__.target_team.id
        self.client.teams[team_id].archive().execute_query()

    def test8_delete_team(self):
        grp_to_delete = self.__class__.target_team
        grp_to_delete.delete_object().execute_query()
