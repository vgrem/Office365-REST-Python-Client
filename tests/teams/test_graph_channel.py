import uuid

from tests.graph_case import GraphTestCase

from office365.graph.teams.team import Team


class TestGraphChannel(GraphTestCase):
    """Tests for channels"""

    target_team = None  # type: Team

    @classmethod
    def setUpClass(cls):
        super(TestGraphChannel, cls).setUpClass()
        grp_name = "Group_" + uuid.uuid4().hex
        result = cls.client.teams.create(grp_name)
        cls.client.execute_query_retry()
        cls.target_team = result.value

    @classmethod
    def tearDownClass(cls):
        pass

    def test1_get_team(self):
        team = self.__class__.target_team
        self.client.load(team)
        self.client.execute_query()
        self.assertIsNotNone(team.id)

    def test2_get_channels(self):
        channels = self.__class__.target_team.channels
        self.client.load(channels)
        self.client.execute_query()
        self.assertGreater(len(channels), 0)
