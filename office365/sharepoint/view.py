from office365.runtime.client_object import ClientObject
from office365.runtime.client_query import DeleteEntityQuery, UpdateEntityQuery
from office365.runtime.resource_path import ResourcePath
from office365.runtime.resource_path_service_operation import ResourcePathServiceOperation
from office365.runtime.serviceOperationQuery import ServiceOperationQuery
from office365.sharepoint.camlQuery import CamlQuery
from office365.sharepoint.view_field_collection import ViewFieldCollection


class View(ClientObject):
    """Specifies a list view."""

    def __init__(self, context, resource_path=None, parent_list=None):
        super(View, self).__init__(context, resource_path, None, None)
        self._parent_list = parent_list

    def get_items(self):
        """Get list items per a view """
        self.ensure_property("viewQuery", self._get_items_inner)
        return self._parent_list.items

    def _get_items_inner(self, target_view):
        caml_query = CamlQuery.parse(target_view.viewQuery)
        qry = ServiceOperationQuery(self._parent_list, "GetItems", None, caml_query, "query", self._parent_list.items)
        self.context.add_query(qry)

    def update(self):
        """Update view"""
        qry = UpdateEntityQuery(self)
        self.context.add_query(qry)

    def delete_object(self):
        """The recommended way to delete a view is to send a DELETE request to the View resource endpoint, as shown
        in View request examples."""
        qry = DeleteEntityQuery(self)
        self.context.add_query(qry)
        self.remove_from_parent_collection()

    @property
    def viewFields(self):
        """Gets a value that specifies the collection of fields in the list view."""
        if self.is_property_available('ViewFields'):
            return self.properties['ViewFields']
        else:
            return ViewFieldCollection(self.context, ResourcePath("ViewFields", self.resource_path))

    @property
    def viewQuery(self):
        """Gets or sets a value that specifies the query that is used by the list view."""
        if self.is_property_available('ViewQuery'):
            return self.properties['ViewQuery']
        else:
            return None

    def set_property(self, name, value, persist_changes=True):
        super(View, self).set_property(name, value, persist_changes)
        # fallback: create a new resource path
        if self._resource_path is None:
            if name == "Id":
                self._resource_path = ResourcePathServiceOperation(
                    "GetById", [value], self._parent_collection.resource_path)
            elif name == "Title":
                self._resource_path = ResourcePathServiceOperation(
                    "GetByTitle", [value], self._parent_collection.resource_path)
