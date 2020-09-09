import uuid

from tests.graph_case import GraphTestCase

from office365.directory.group import Group
from office365.directory.groupProfile import GroupProfile


class TestGraphTeam(GraphTestCase):
    """Tests for teams"""

    target_group = None  # type: Group

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        grp_name = "Group_" + uuid.uuid4().hex
        properties = GroupProfile(grp_name)
        properties.securityEnabled = False
        properties.mailEnabled = True
        properties.groupTypes = ["Unified"]
        cls.target_group = cls.client.groups.add(properties).execute_query()

    def test1_get_all_teams(self):
        teams = self.client.teams.get_all().execute_query()
        self.assertGreater(len(teams), 0)

    def test2_ensure_team(self):
        team_id = self.__class__.target_group.id
        teams = self.client.me.joinedTeams.filter("id eq '{0}'".format(team_id)).get().execute_query()
        self.assertIsNotNone(teams.resource_path)

        if len(teams) == 0:
            new_team = self.__class__.target_group.add_team().execute_query_retry()
            self.assertIsNotNone(new_team.id)
        else:
            self.assertEqual(len(teams), 1)

    def test3_get_team(self):
        group_id = self.__class__.target_group.id
        existing_team = self.client.teams[group_id].get().execute_query()
        self.assertIsNotNone(existing_team.resource_url)
        self.assertIsNotNone(existing_team.messagingSettings)

        if existing_team.properties["isArchived"]:
            existing_team.unarchive()
            self.client.load(existing_team)
            self.client.execute_query()
            self.assertFalse(existing_team.properties["isArchived"])

    def test4_update_team(self):
        team_id = self.__class__.target_group.properties['id']
        team_to_update = self.client.teams[team_id]
        team_to_update.funSettings.allowGiphy = False
        team_to_update.update().execute_query()

    def test5_archive_team(self):
        group_id = self.__class__.target_group.id
        team_to_archive = self.client.teams[group_id]
        team_to_archive.archive().execute_query()

    def test6_delete_group_with_team(self):
        grp_to_delete = self.__class__.target_group
        grp_to_delete.delete_object(True).execute_query()
