from office365.runtime.client_object import ClientObject
from office365.runtime.client_query import ClientQuery
from office365.runtime.resource_path_entry import ResourcePathEntry


class OutlookEntity(ClientObject):
    """Base Outlook entity."""

    def update(self):
        qry = ClientQuery.update_entry_query(self)
        self.context.add_query(qry)

    def delete_object(self):
        """Deletes the outlook entity."""
        qry = ClientQuery.delete_entry_query(self)
        self.context.add_query(qry)

    @property
    def resource_path(self):
        orig_path = ClientObject.resource_path.fget(self)
        if self.is_property_available("Id") and orig_path is None:
            return ResourcePathEntry(self.context,
                                     self._parent_collection.resource_path,
                                     self.properties["Id"])
        return orig_path

