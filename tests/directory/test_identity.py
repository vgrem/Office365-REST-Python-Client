from unittest import TestCase

from office365.graph_client import GraphClient
from tests import test_client_id, test_client_secret, test_tenant


class TestIdentity(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = GraphClient.with_client_secret(
            test_tenant, test_client_id, test_client_secret
        )

    def test1_list_identity_providers(self):
        result = self.client.identity.identity_providers.get().execute_query()
        self.assertIsNotNone(result.resource_path)

    def test2_list_user_flows(self):
        result = self.client.identity.b2x_user_flows.get().execute_query()
        self.assertIsNotNone(result.resource_path)

    def test3_available_provider_types(self):
        result = (
            self.client.identity.identity_providers.available_provider_types().execute_query()
        )
        self.assertIsNotNone(result.value)

    # def test4_list_risky_users(self):
    #    result = self.client.identity_protection.risky_users.get().execute_query()
    #    self.assertIsNotNone(result.resource_path)
