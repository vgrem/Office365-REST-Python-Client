from office365.runtime.client_object_collection import ClientObjectCollection
from office365.runtime.client_query import ServiceOperationQuery
from office365.runtime.resource_path_service_operation import ResourcePathServiceOperation
from office365.sharepoint.view import View


class ViewCollection(ClientObjectCollection):
    """Represents a collection of View resources."""
    def __init__(self, context, resource_path=None):
        super(ViewCollection, self).__init__(context, View, resource_path)

    def add(self, view_creation_information):
        view = View(self.context)
        view._parent_collection = self
        qry = ServiceOperationQuery(self, "Add", None, view_creation_information, "parameters", view)
        self.context.add_query(qry)
        return view

    def get_by_title(self, view_title):
        """Gets the list view with the specified title."""
        return View(self.context,
                    ResourcePathServiceOperation("GetByTitle", [view_title], self.resourcePath))

    def get_by_id(self, view_id):
        """Gets the list view with the specified ID."""
        return View(self.context,
                    ResourcePathServiceOperation("GetById", [view_id], self.resourcePath))
