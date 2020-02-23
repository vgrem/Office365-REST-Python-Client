import uuid
from office365.directory.groupCreationProperties import GroupCreationProperties
from office365.runtime.client_request_exception import ClientRequestException
from tests.graph_case import GraphTestCase


class TestGraphUser(GraphTestCase):
    """Tests for Azure Active Directory (Azure AD) users"""

    def test1_get_user_list(self):
        users = self.client.users.top(1)
        self.client.load(users)
        self.client.execute_query()
        self.assertEquals(len(users), 1)
        for user in users:
            self.assertIsNotNone(user.properties['id'])
