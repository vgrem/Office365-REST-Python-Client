from unittest import TestCase

from office365.graph_client import GraphClient
from tests.graph_case import acquire_token_by_client_credentials


class TestIdentity(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.client = GraphClient(acquire_token_by_client_credentials)

    def test1_list_identity_providers(self):
        result = self.client.identity.identity_providers.get().execute_query()
        self.assertIsNotNone(result.resource_path)

    def test2_list_user_flows(self):
        result = self.client.identity.b2x_user_flows.get().execute_query()
        self.assertIsNotNone(result.resource_path)

    def test3_available_provider_types(self):
        result = self.client.identity.identity_providers.available_provider_types().execute_query()
        self.assertIsNotNone(result.value)


