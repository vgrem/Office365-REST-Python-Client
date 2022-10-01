from office365.directory.object import DirectoryObject


class PolicyBase(DirectoryObject):
    """Represents an abstract base type for policy types to inherit from"""

    @property
    def display_name(self):
        """
        Display name for this policy

        :rtype: str or None
        """
        return self.properties.get("displayName", None)
