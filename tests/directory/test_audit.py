from unittest import TestCase

from office365.graph_client import GraphClient
from tests.graph_case import acquire_token_by_client_credentials


class TestAudit(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.client = GraphClient(acquire_token_by_client_credentials)

    def test1_list_signins(self):
        col = self.client.audit_logs.signins.top(10).get().execute_query()
        self.assertIsNotNone(col.resource_path)

    def test2_list_directory_audits(self):
        col = self.client.audit_logs.directory_audits.top(10).get().execute_query()
        self.assertIsNotNone(col.resource_path)
