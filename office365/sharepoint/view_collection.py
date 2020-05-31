from office365.runtime.client_object_collection import ClientObjectCollection
from office365.runtime.resource_path_service_operation import ResourcePathServiceOperation
from office365.runtime.serviceOperationQuery import ServiceOperationQuery
from office365.sharepoint.view import View


class ViewCollection(ClientObjectCollection):
    """Represents a collection of View resources."""

    def __init__(self, context, resource_path=None, parent_list=None):
        super(ViewCollection, self).__init__(context, View, resource_path)
        self._parent_list = parent_list

    def add(self, view_creation_information):
        view = View(self.context, None, self._parent_list)
        view._parent_collection = self
        qry = ServiceOperationQuery(self, "Add", None, view_creation_information, "parameters", view)
        self.context.add_query(qry)
        return view

    def get_by_title(self, view_title):
        """Gets the list view with the specified title."""
        return View(self.context,
                    ResourcePathServiceOperation("GetByTitle", [view_title], self.resource_path), self._parent_list)

    def get_by_id(self, view_id):
        """Gets the list view with the specified ID."""
        return View(self.context,
                    ResourcePathServiceOperation("GetById", [view_id], self.resource_path), self._parent_list)
