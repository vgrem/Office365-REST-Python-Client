from unittest import TestCase

from office365.graph_client import GraphClient
from tests import test_tenant
from tests.graph_case import acquire_token_by_client_credentials


class TestTenant(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = GraphClient(acquire_token_by_client_credentials)

    def test1_find_tenant_information(self):
        result = (
            self.client.tenant_relationships.find_tenant_information_by_domain_name(
                test_tenant
            ).execute_query()
        )
        self.assertIsNotNone(result.value)
