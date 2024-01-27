from office365.intune.devices.device import Device
from tests.graph_case import GraphTestCase


class TestDevices(GraphTestCase):
    device = None  # type: Device

    @classmethod
    def setUpClass(cls):
        super(TestDevices, cls).setUpClass()

    @classmethod
    def tearDownClass(cls):
        pass

    def test1_get_device_management(self):
        result = self.client.device_management.get().execute_query()
        self.assertIsNotNone(result.resource_path)

    def test2_get_my_managed_devices(self):
        result = self.client.me.managed_devices.get().execute_query()
        self.assertIsNotNone(result.resource_path)

    def test3_list_devices(self):
        result = self.client.devices.get().execute_query()
        self.assertIsNotNone(result.resource_path)

    def test4_create_device(self):
        result = self.client.devices.add("Test device", "linux", "1").execute_query()
        self.assertIsNotNone(result.resource_path)
        self.__class__.device = result

    def test5_delete_device(self):
        self.__class__.device.delete_object().execute_query()
