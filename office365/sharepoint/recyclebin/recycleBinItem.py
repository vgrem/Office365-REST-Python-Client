from office365.runtime.queries.delete_entity_query import DeleteEntityQuery
from office365.runtime.queries.service_operation_query import ServiceOperationQuery
from office365.runtime.resource_path import ResourcePath
from office365.runtime.resource_path_service_operation import ResourcePathServiceOperation
from office365.sharepoint.base_entity import BaseEntity
from office365.sharepoint.principal.user import User


class RecycleBinItem(BaseEntity):

    def delete_object(self):
        """Permanently deletes the Recycle Bin item."""
        qry = DeleteEntityQuery(self)
        self.context.add_query(qry)
        self.remove_from_parent_collection()
        return self

    def restore(self):
        """Restores the Recycle Bin item to its original location."""
        qry = ServiceOperationQuery(self, "Restore")
        self.context.add_query(qry)
        return self

    def move_to_second_stage(self):
        qry = ServiceOperationQuery(self, "MoveToSecondStage")
        self.context.add_query(qry)
        return self

    @property
    def id(self):
        """Gets a value that specifies the identifier of the Recycle Bin item."""
        return self.properties.get('Id', None)

    @property
    def deleted_by(self):
        """Gets a value that specifies the user who deleted the Recycle Bin item."""
        return self.properties.get('DeletedBy', User(self.context, ResourcePath("DeletedBy", self.resource_path)))

    @property
    def deleted_date(self):
        """Gets a value that specifies when the Recycle Bin item was moved to the Recycle Bin."""
        return self.properties.get('DeletedDate', None)

    def set_property(self, name, value, persist_changes=True):
        super(RecycleBinItem, self).set_property(name, value, persist_changes)
        # fallback: create a new resource path
        if self._resource_path is None:
            if name == "Id" and self._parent_collection is not None:
                self._resource_path = ResourcePathServiceOperation(
                    "GetById", [value], self._parent_collection.resource_path)
