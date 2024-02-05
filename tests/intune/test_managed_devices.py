from tests.graph_case import GraphTestCase


class TestManagedDevices(GraphTestCase):
    @classmethod
    def setUpClass(cls):
        super(TestManagedDevices, cls).setUpClass()

    @classmethod
    def tearDownClass(cls):
        pass

    # def test1_create(self):
    #    result = self.client.device_management.managed_devices.add().execute_query()
    #    self.assertIsNotNone(result.resource_path)

    def test2_get_my(self):
        result = self.client.me.managed_devices.get().execute_query()
        self.assertIsNotNone(result.resource_path)
