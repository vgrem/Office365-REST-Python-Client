from office365.communications.presences.presence import Presence
from tests.graph_case import GraphTestCase


class TestPresence(GraphTestCase):
    target_presence = None  # type: Presence

    @classmethod
    def setUpClass(cls):
        super(TestPresence, cls).setUpClass()

    @classmethod
    def tearDownClass(cls):
        pass

    def test1_set_my_preferred_presence(self):
        my_presence = self.client.me.presence
        my_presence.set_user_preferred_presence().execute_query()
        self.assertIsNotNone(my_presence.resource_path)

    def test2_get_presences_by_user_id(self):
        me = self.client.me.get().execute_query()
        presences = self.client.communications.get_presences_by_user_id([me.id]).execute_query()
        self.assertIsNotNone(presences.resource_path)

    def test3_clear_my_presence(self):
        my_presence = self.client.me.presence
        my_presence.clear_user_preferred_presence().execute_query()
        self.assertIsNotNone(my_presence.resource_path)
