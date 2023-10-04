from unittest import TestCase

from office365.graph_client import GraphClient
from tests.graph_case import acquire_token_by_client_credentials


class TestIdentityGovernance(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = GraphClient(acquire_token_by_client_credentials)

    def test1_list_app_consent_requests(self):
        result = (
            self.client.identity_governance.app_consent.app_consent_requests.get().execute_query()
        )
        self.assertIsNotNone(result.resource_path)
