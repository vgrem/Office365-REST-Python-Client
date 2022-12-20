from office365.runtime.queries.service_operation import ServiceOperationQuery
from office365.runtime.paths.resource_path import ResourcePath
from office365.runtime.paths.service_operation import ServiceOperationPath
from office365.sharepoint.base_entity import BaseEntity
from office365.sharepoint.principal.users.user import User


class RecycleBinItem(BaseEntity):
    """Represents a Recycle Bin item in the Recycle Bin of a site or a site collection."""

    def restore(self):
        """Restores the Recycle Bin item to its original location."""
        qry = ServiceOperationQuery(self, "Restore")
        self.context.add_query(qry)
        return self

    def move_to_second_stage(self):
        """
        Moves the Recycle Bin item from the first-stage Recycle Bin to the second-stage Recycle Bin if the
        SecondStageRecycleBinQuota property on the current web application is not 0. Otherwise, deletes the item.
        """
        qry = ServiceOperationQuery(self, "MoveToSecondStage")
        self.context.add_query(qry)
        return self

    @property
    def id(self):
        """Gets a value that specifies the identifier of the Recycle Bin item."""
        return self.properties.get('Id', None)

    @property
    def size(self):
        """Gets a value that specifies the size of the Recycle Bin item in bytes.

        :rtype: long or None
        """
        return self.properties.get('Size', None)

    @property
    def author(self):
        """
        Gets a value that specifies the user who created the Recycle Bin item.
        """
        return self.properties.get("Author", User(self.context, ResourcePath("Author", self.resource_path)))

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
                self._resource_path = ServiceOperationPath("GetById", [value], self._parent_collection.resource_path)
