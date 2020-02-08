from office365.runtime.client_object import ClientObject
from office365.runtime.client_query import DeleteEntityQuery


class DirectoryObject(ClientObject):
    """Represents an Azure Active Directory object. The directoryObject type is the base type for many other
    directory entity types. """

    def delete_object(self):
        """Deletes the directory object."""
        qry = DeleteEntityQuery(self)
        self.context.add_query(qry)
        self.remove_from_parent_collection()

    @property
    def deletedDateTime(self):
        """ETag for the item."""
        if self.is_property_available("deletedDateTime"):
            return self.properties['deletedDateTime']
        return None
