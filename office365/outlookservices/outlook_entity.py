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

    @property
    def resourcePath(self):
        resource_path = super(OutlookEntity, self).resourcePath
        if resource_path:
            return resource_path

        # fallback: create a new resource path
        if self.is_property_available("Id"):
            return ResourcePathEntity(
                self.context,
                self._parent_collection.resourcePath,
                self.properties["Id"])
