from office365.directory.object import DirectoryObject
from office365.runtime.paths.resource_path import ResourcePath


class DirectoryRole(DirectoryObject):
    """Represents an Azure AD directory role. Azure AD directory roles are also known as administrator roles """

    @property
    def description(self):
        """The description for the directory role.
        :rtype: str or None
        """
        return self.properties.get("Description", None)

    @property
    def display_name(self):
        """The display name for the directory role.
        :rtype: str or None
        """
        return self.properties.get("displayName", None)

    @property
    def members(self):
        """
        Users that are members of this directory role.
        """
        from office365.directory.object_collection import DirectoryObjectCollection
        return self.properties.get('members',
                                   DirectoryObjectCollection(self.context, ResourcePath("members", self.resource_path)))
