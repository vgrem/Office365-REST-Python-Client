from unittest import TestCase

from office365.graph_client import GraphClient
from tests import test_client_id, test_client_secret, test_tenant


class TestInvitations(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = GraphClient(tenant=test_tenant).with_client_secret(
            test_client_id, test_client_secret
        )

    def test1_create_invitation(self):
        invitation = self.client.invitations.create(
            "admin@fabrikam.com", "https://myapp.contoso.com"
        ).execute_query()
        self.assertIsNotNone(invitation.resource_path)
