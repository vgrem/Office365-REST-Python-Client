from unittest import TestCase

from office365.graph_client import GraphClient
from tests import test_client_id, test_client_secret, test_tenant


class TestOrganization(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = GraphClient(tenant=test_tenant).with_client_secret(
            test_client_id, test_client_secret
        )

    def test1_list(self):
        org = self.client.organization.get().execute_query()
        self.assertIsNotNone(org.resource_path)

    def test2_list_contacts(self):
        result = self.client.contacts.get().top(10).execute_query()
        self.assertIsNotNone(result.resource_path)
