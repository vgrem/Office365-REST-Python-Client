from tests.graph_case import GraphTestCase


class TestDevices(GraphTestCase):

    @classmethod
    def setUpClass(cls):
        super(TestDevices, cls).setUpClass()

    @classmethod
    def tearDownClass(cls):
        pass

    def test1_create_plan(self):
        result = self.client.device_management.get().execute_query()
        self.assertIsNotNone(result.resource_path)

