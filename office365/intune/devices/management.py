from office365.entity import Entity
from office365.entity_collection import EntityCollection
from office365.intune.audit.event import AuditEventCollection
from office365.intune.devices.managed import ManagedDevice
from office365.runtime.paths.resource_path import ResourcePath


class DeviceManagement(Entity):
    """
    The deviceManagement resource represents a tenant's collection device identities that have been pre-staged in
    Intune, and the enrollment profiles that may be assigned to device identities that support pre-enrollment
    configuration.
    """

    @property
    def audit_events(self):
        """"""
        return self.properties.get("auditEvents", AuditEventCollection(self.context,
                                                                       ResourcePath("auditEvents", self.resource_path)))

    @property
    def managed_devices(self):
        """"""
        return self.properties.get('managedDevices',
                                   EntityCollection(self.context, ManagedDevice,
                                                    ResourcePath("managedDevices", self.resource_path)))

    def get_property(self, name, default_value=None):
        if default_value is None:
            property_mapping = {
                "auditEvents": self.audit_events,
                "managedDevices": self.managed_devices
            }
            default_value = property_mapping.get(name, None)
        return super(DeviceManagement, self).get_property(name, default_value)
