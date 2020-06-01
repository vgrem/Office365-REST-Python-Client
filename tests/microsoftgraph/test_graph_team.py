import unittest

from tests.microsoftgraph.graph_case import GraphTestCase


class TestGraphTeam(GraphTestCase):
    """Tests for teams"""

    target_group = None

    @classmethod
    def setUpClass(cls):
        super(TestGraphTeam, cls).setUpClass()
        result = cls.client.groups.filter("groupTypes/any(c:c eq 'Unified')").top(1)
        cls.client.load(result)
        cls.client.execute_query()
        cls.target_group = result[0]

    @unittest.skipIf(target_group is None, "Group does not exist")
    def test2_ensure_team(self):
        group_id = self.__class__.target_group.properties['id']
        teams = self.client.me.joinedTeams.filter("id eq '{0}'".format(group_id))
        self.client.load(teams)
        self.client.execute_query()
        self.assertIsNotNone(teams.resource_path)

        if len(teams) == 0:
            new_team = self.__class__.target_group.add_team()
            self.client.execute_query()
            self.assertIsNotNone(new_team)
        else:
            self.assertEqual(len(teams), 1)

    @unittest.skipIf(target_group is None, "Group does not exist")
    def test3_get_team(self):
        group_id = self.__class__.target_group.properties['id']
        existing_team = self.client.teams[group_id]
        self.client.load(existing_team)
        self.client.execute_query()
        self.assertIsNotNone(existing_team.resource_url)
        self.assertIsNotNone(existing_team.messagingSettings)

        if existing_team.properties["isArchived"]:
            existing_team.unarchive()
            self.client.load(existing_team)
            self.client.execute_query()
            self.assertFalse(existing_team.properties["isArchived"])

    @unittest.skipIf(target_group is None, "Group does not exist")
    def test4_update_team(self):
        group_id = self.__class__.target_group.properties['id']
        team_to_update = self.client.teams[group_id]
        team_to_update.funSettings.allowGiphy = False
        team_to_update.update()
        self.client.execute_query()

    @unittest.skipIf(target_group is None, "Group does not exist")
    def test5_archive_team(self):
        group_id = self.__class__.target_group.properties['id']
        team_to_archive = self.client.teams[group_id]
        team_to_archive.archive()
        self.client.execute_query()
