import uuid
from office365.directory.groupCreationProperties import GroupCreationProperties
from office365.runtime.client_request_exception import ClientRequestException
from tests.graph_case import GraphTestCase


class TestGraphTeam(GraphTestCase):
    """Tests for teams"""

    def test1_list_teams(self):
        teams = self.client.me.joinedTeams
        self.client.load(teams)
        self.client.execute_query()




