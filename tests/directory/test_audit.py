from unittest import TestCase

import msal

from office365.graph_client import GraphClient
from tests import load_settings
from tests.graph_case import acquire_token_by_client_credentials


class TestAudit(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.client = GraphClient(acquire_token_by_client_credentials)

    def test1_list_signins(self):
        col = self.client.audit_logs.signins.top(10).get().execute_query()
        self.assertIsNotNone(col.resource_path)
