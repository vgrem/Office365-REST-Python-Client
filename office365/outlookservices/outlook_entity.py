from office365.runtime.client_object import ClientObject
from office365.runtime.client_query import ClientQuery
from office365.runtime.resource_path_entity import ResourcePathEntity


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
        resource_path = super(OutlookEntity, self).resource_path
        if resource_path:
            return resource_path

        # fallback: create a new resource path
        if self.is_property_available("Id"):
            return ResourcePathEntity(
                self.context,
                self._parent_collection.resource_path,
                self.properties["Id"])
