from office365.runtime.client_object import ClientObject


class DirectoryObject(ClientObject):
    """Represents an Azure Active Directory object. The directoryObject type is the base type for many other
    directory entity types. """

    @property
    def deletedDateTime(self):
        """ETag for the item."""
        if self.is_property_available("deletedDateTime"):
            return self.properties['deletedDateTime']
        return None
