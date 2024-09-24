from office365.graph_client import GraphClient
from tests import test_tenant, test_client_id, test_client_secret
from tests.graph_case import GraphTestCase


class TestCallRecord(GraphTestCase):

    @classmethod
    def setUpClass(cls):
        super(TestCallRecord, cls).setUpClass()
        cls.app_client = GraphClient.with_client_secret(
            test_tenant, test_client_id, test_client_secret
        )

    @classmethod
    def tearDownClass(cls):
        pass

    def test1_get_direct_routing_calls(self):
        result = (
            self.app_client.communications.call_records.get_direct_routing_calls().execute_query()
        )
        self.assertIsNotNone(result.value)
