from unittest import TestCase

from office365.graph_client import GraphClient
from tests import test_client_id, test_client_secret, test_tenant


class TestIdentityGovernance(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = GraphClient.with_client_secret(
            test_tenant, test_client_id, test_client_secret
        )

    def test1_list_app_consent_requests(self):
        result = (
            self.client.identity_governance.app_consent.app_consent_requests.get().execute_query()
        )
        self.assertIsNotNone(result.resource_path)
