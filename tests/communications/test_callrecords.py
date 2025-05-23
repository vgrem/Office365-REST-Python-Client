from office365.graph_client import GraphClient
from tests import test_client_id, test_client_secret, test_tenant
from tests.graph_case import GraphTestCase


class TestCallRecord(GraphTestCase):

    @classmethod
    def setUpClass(cls):
        super(TestCallRecord, cls).setUpClass()
        cls.app_client = GraphClient(tenant=test_tenant).with_client_secret(
            test_client_id, test_client_secret
        )

    @classmethod
    def tearDownClass(cls):
        pass

    #def test1_create_peer_to_peer_call(self):
    #    result = self.client.communications.calls.create("https://bot.mediadev8.com/callback").execute_query()
    #    self.assertIsNotNone(result.resource_path)

    def test2_get_direct_routing_calls(self):
        result = (
            self.app_client.communications.call_records.get_direct_routing_calls().execute_query()
        )
        self.assertIsNotNone(result.value)
