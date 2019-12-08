from office365.directory.directory_object import DirectoryObject
from office365.directory.directory_object_collection import DirectoryObjectCollection
from office365.runtime.resource_path_entity import ResourcePathEntity


class Group(DirectoryObject):
    """Represents an Azure Active Directory (Azure AD) group, which can be an Office 365 group, or a security group."""

    @property
    def members(self):
        """Users and groups that are members of this group."""
        if self.is_property_available('members'):
            return self.properties['members']
        else:
            return DirectoryObjectCollection(self.context,
                                             ResourcePathEntity(self.context, self.resource_path, "members"))

    @property
    def owners(self):
        """The owners of the group."""
        if self.is_property_available('owners'):
            return self.properties['owners']
        else:
            return DirectoryObjectCollection(self.context,
                                             ResourcePathEntity(self.context, self.resource_path, "owners"))
