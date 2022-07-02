from office365.directory.directory_object import DirectoryObject
from office365.runtime.paths.resource_path import ResourcePath


class DirectoryRole(DirectoryObject):
    """Represents an Azure AD directory role. Azure AD directory roles are also known as administrator roles """

    @property
    def members(self):
        """
        Users that are members of this directory role. HTTP Methods: GET, POST, DELETE. Read-only. Nullable.

        :rtype: office365.directory.directory_object_collection.DirectoryObjectCollection
        """
        from office365.directory.directory_object_collection import DirectoryObjectCollection
        return self.get_property('members',
                                 DirectoryObjectCollection(self.context, ResourcePath("members", self.resource_path)))
