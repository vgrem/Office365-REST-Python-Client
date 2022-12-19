from office365.directory.object import DirectoryObject
from office365.directory.object_collection import DirectoryObjectCollection
from office365.runtime.paths.resource_path import ResourcePath


class Device(DirectoryObject):
    """
    Represents a device registered in the organization. Devices are created in the cloud using the
    Device Registration Service or by Intune. They're used by conditional access policies for multi-factor
    authentication. These devices can range from desktop and laptop machines to phones and tablets.
    """

    def get_property(self, name, default_value=None):
        if default_value is None:
            property_mapping = {
                "memberOf": self.member_of,
                "registeredOwners": self.registered_owners,
                "registeredUsers": self.registered_users,
                "transitiveMemberOf": self.transitive_member_of
            }
            default_value = property_mapping.get(name, None)
        return super(Device, self).get_property(name, default_value)

    @property
    def member_of(self):
        """Groups and administrative units that this device is a member of."""
        return self.properties.get('memberOf',
                                   DirectoryObjectCollection(self.context,
                                                             ResourcePath("memberOf", self.resource_path)))

    @property
    def registered_owners(self):
        """The user that cloud joined the device or registered their personal device.
        The registered owner is set at the time of registration. Currently, there can be only one owner."""
        return self.properties.get('registeredOwners',
                                   DirectoryObjectCollection(self.context,
                                                             ResourcePath("registeredOwners", self.resource_path)))

    @property
    def registered_users(self):
        """Collection of registered users of the device. For cloud joined devices and registered personal devices,
        registered users are set to the same value as registered owners at the time of registration."""
        return self.properties.get('registeredUsers',
                                   DirectoryObjectCollection(self.context,
                                                             ResourcePath("registeredUsers", self.resource_path)))

    @property
    def transitive_member_of(self):
        """Get groups, directory roles that the user is a member of. This API request is transitive, and will also
        return all groups the user is a nested member of. """
        return self.properties.get('transitiveMemberOf',
                                   DirectoryObjectCollection(self.context,
                                                             ResourcePath("transitiveMemberOf", self.resource_path)))
