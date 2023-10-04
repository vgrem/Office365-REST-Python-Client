from unittest import TestCase

from office365.graph_client import GraphClient
from tests.graph_case import acquire_token_by_client_credentials


class TestInvitations(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = GraphClient(acquire_token_by_client_credentials)

    def test1_create_invitation(self):
        invitation = self.client.invitations.create(
            "admin@fabrikam.com", "https://myapp.contoso.com"
        ).execute_query()
        self.assertIsNotNone(invitation.resource_path)
