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

    def test3_list_devices(self):
        result = self.client.devices.get().execute_query()
        self.assertIsNotNone(result.resource_path)

    def test4_create_device(self):
        result = self.client.devices.add("Test device", "linux", "1").execute_query()
        self.assertIsNotNone(result.resource_path)
        self.__class__.device = result

    def test5_create_registered_owner(self):
        result = self.__class__.device.registered_owners.add(
            self.client.me
        ).execute_query()
        self.assertIsNotNone(result.resource_path)

    def test6_list_registered_owners(self):
        result = self.__class__.device.registered_owners.get().execute_query()
        self.assertIsNotNone(result.resource_path)

    def test7_delete_device(self):
        self.__class__.device.delete_object().execute_query()
