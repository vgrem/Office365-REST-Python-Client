from office365.runtime.client_object import ClientObject
from office365.runtime.client_query import ClientQuery, UpdateEntityQuery, DeleteEntityQuery
from office365.runtime.resource_path_entity import ResourcePathEntity


class OutlookEntity(ClientObject):
    """Base Outlook entity."""

    def update(self):
        qry = UpdateEntityQuery(self)
        self.context.add_query(qry)

    def delete_object(self):
        """Deletes the outlook entity."""
        qry = DeleteEntityQuery(self)
        self.context.add_query(qry)

    def set_property(self, name, value, serializable=True):
        super(OutlookEntity, self).set_property(name, value, serializable)
        # fallback: create a new resource path
        if name == "Id":
            self._resource_path = ResourcePathEntity(
                self.context,
                self._parent_collection.resourcePath,
                value)
