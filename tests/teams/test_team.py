import uuid

from tests.graph_case import GraphTestCase

from office365.directory.group import Group
from office365.directory.group_profile import GroupProfile


def _create_group(client):
    grp_name = "Group_" + uuid.uuid4().hex
    properties = GroupProfile(grp_name)
    properties.securityEnabled = False
    properties.mailEnabled = True
    properties.groupTypes = ["Unified"]
    return client.groups.add(properties)


class TestGraphTeam(GraphTestCase):
    """Tests for teams"""

    target_group = None  # type: Group

    @classmethod
    def setUpClass(cls):
        super(TestGraphTeam, cls).setUpClass()

    def test1_ensure_team(self):
        self.__class__.target_group = _create_group(self.client).execute_query()
        new_team = self.__class__.target_group.add_team().execute_query_retry()
        self.assertIsNotNone(new_team.id)

    def test3_get_all_teams(self):
        teams = self.client.teams.get_all().execute_query()
        self.assertGreater(len(teams), 0)

    def test4_get_joined_teams(self):
        my_teams = self.client.me.joined_teams.get().execute_query()
        self.assertIsNotNone(my_teams.resource_path)
        self.assertGreater(len(my_teams), 0)

    def test5_get_team(self):
        group_id = self.__class__.target_group.id
        existing_team = self.client.teams[group_id].get().execute_query()
        self.assertIsNotNone(existing_team.resource_url)
        self.assertIsNotNone(existing_team.messagingSettings)

        if existing_team.properties["isArchived"]:
            existing_team.unarchive()
            self.client.load(existing_team)
            self.client.execute_query()
            self.assertFalse(existing_team.properties["isArchived"])

    def test6_update_team(self):
        team_id = self.__class__.target_group.properties['id']
        team_to_update = self.client.teams[team_id]
        team_to_update.funSettings.allowGiphy = False
        team_to_update.update().execute_query()

    def test7_archive_team(self):
        group_id = self.__class__.target_group.id
        self.client.teams[group_id].archive().execute_query()

    def test8_delete_team(self):
        grp_to_delete = self.__class__.target_group
        grp_to_delete.delete_object(True).execute_query()
