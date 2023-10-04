from unittest import TestCase

from office365.graph_client import GraphClient
from tests.graph_case import acquire_token_by_client_credentials


class TestOrganization(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = GraphClient(acquire_token_by_client_credentials)

    def test1_list(self):
        org = self.client.organization.get().execute_query()
        self.assertIsNotNone(org.resource_path)

    def test2_list_contacts(self):
        result = self.client.contacts.get().top(10).execute_query()
        self.assertIsNotNone(result.resource_path)
