from office365.entity import Entity
from office365.intune.devices.category import DeviceCategory
from office365.runtime.paths.resource_path import ResourcePath
from office365.runtime.queries.service_operation import ServiceOperationQuery


class ManagedDevice(Entity):
    """Devices that are managed or pre-enrolled through Intune"""

    def locate_device(self):
        """Locate a device"""
        qry = ServiceOperationQuery(self, "locateDevice")
        self.context.add_query(qry)
        return self

    @property
    def device_category(self):
        """	Device category"""
        return self.properties.get('deviceCategory', DeviceCategory(self.context,
                                                                    ResourcePath("deviceCategory", self.resource_path)))

    @property
    def manufacturer(self):
        """
        Manufacturer of the device.
        :rtype: str
        """
        return self.properties.get("manufacturer", None)

    @property
    def operating_system(self):
        """
        Manufacturer of the device.
        :rtype: str
        """
        return self.properties.get("operatingSystem", None)

    @property
    def users(self):
        """The primary users associated with the managed device."""
        from office365.directory.users.collection import UserCollection
        return self.properties.get('users', UserCollection(self.context, ResourcePath("users", self.resource_path)))

    def get_property(self, name, default_value=None):
        if default_value is None:
            property_mapping = {
                "deviceCategory": self.device_category
            }
            default_value = property_mapping.get(name, None)
        return super(ManagedDevice, self).get_property(name, default_value)
