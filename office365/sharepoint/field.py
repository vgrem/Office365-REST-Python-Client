from office365.runtime.client_object import ClientObject
from office365.runtime.client_query import UpdateEntityQuery, DeleteEntityQuery
from office365.runtime.resource_path_service_operation import ResourcePathServiceOperation


class Field(ClientObject):
    """Represents a field in a SharePoint Web site"""

    def update(self):
        """Update the field."""
        qry = UpdateEntityQuery(self)
        self.context.add_query(qry)

    def delete_object(self):
        """Deletes the field."""
        qry = DeleteEntityQuery(self)
        self.context.add_query(qry)
        self.remove_from_parent_collection()

    def set_property(self, name, value, persist_changes=True):
        super(Field, self).set_property(name, value, persist_changes)
        # fallback: create a new resource path
        if name == "Id" and self._resource_path is None:
            self._resource_path = ResourcePathServiceOperation(
                "getById", [value], self._parent_collection.resourcePath)
