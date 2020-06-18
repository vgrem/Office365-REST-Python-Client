from office365.runtime.client_query import DeleteEntityQuery
from office365.runtime.resource_path_service_operation import ResourcePathServiceOperation
from office365.runtime.serviceOperationQuery import ServiceOperationQuery
from office365.sharepoint.base_entity import BaseEntity


class Field(BaseEntity):
    """Represents a field in a SharePoint Web site"""

    def set_show_in_display_form(self, flag):
        """Sets the value of the ShowInDisplayForm property for this field."""
        qry = ServiceOperationQuery(self, "setShowInDisplayForm", [flag])
        self.context.add_query(qry)

    def set_show_in_edit_form(self, flag):
        """Sets the value of the ShowInEditForm property for this field."""
        qry = ServiceOperationQuery(self, "setShowInEditForm", [flag])
        self.context.add_query(qry)

    def set_show_in_new_form(self, flag):
        """Sets the value of the ShowInNewForm property for this field."""
        qry = ServiceOperationQuery(self, "setShowInNewForm", [flag])
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
                "getById", [value], self._parent_collection.resource_path)
