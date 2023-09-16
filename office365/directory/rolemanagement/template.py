from office365.directory.object import DirectoryObject


class DirectoryRoleTemplate(DirectoryObject):
    """Represents a directory role template. A directory role template specifies the property values of a directory
    role (directoryRole). """

    @property
    def display_name(self):
        """
        The display name to set for the directory role
        :rtype: str
        """
        return self.properties.get("displayName", None)

    @property
    def description(self):
        """
        The display name to set for the directory role
        :rtype: str
        """
        return self.properties.get("description", None)
