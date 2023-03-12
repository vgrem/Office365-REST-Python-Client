from office365.entity import Entity
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
    def users(self):
        """The primary users associated with the managed device."""
        from office365.directory.users.collection import UserCollection
        return self.properties.get('users', UserCollection(self.context, ResourcePath("users", self.resource_path)))
