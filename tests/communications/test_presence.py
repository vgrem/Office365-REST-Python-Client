from tests.graph_case import GraphTestCase


class TestPresence(GraphTestCase):

    @classmethod
    def setUpClass(cls):
        super(TestPresence, cls).setUpClass()

    @classmethod
    def tearDownClass(cls):
        pass

    def test1_get_presences_by_user_id(self):
        me = self.client.me.get().execute_query()
        presences = self.client.communications.get_presences_by_user_id([me.id]).execute_query()
        self.assertIsNotNone(presences.resource_path)

