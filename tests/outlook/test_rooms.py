from unittest import TestCase

from office365.graph_client import GraphClient
from tests import test_client_id, test_client_secret, test_tenant


class TestRooms(TestCase):
    """Tests for Rooms"""

    @classmethod
    def setUpClass(cls):
        cls.client = GraphClient(tenant=test_tenant).with_client_secret(
            test_client_id, test_client_secret
        )

    def test1_get_room_lists(self):
        result = self.client.room_lists.get().execute_query()
        self.assertIsNotNone(result.resource_path)
