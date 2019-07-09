from office365.runtime.client_object_collection import ClientObjectCollection
from office365.runtime.resource_path_service_operation import ResourcePathServiceOperation
from office365.sharepoint.view import View


class ViewCollection(ClientObjectCollection):
    """Represents a collection of View resources."""

    # The object type this collection holds
    item_type = View

    def get_by_title(self, view_title):
        """Gets the list view with the specified title."""
        return View(self.context,
                    ResourcePathServiceOperation(self.context, self.resource_path, "GetByTitle", [view_title]))

    def get_by_id(self, view_id):
        """Gets the list view with the specified ID."""
        return View(self.context,
                    ResourcePathServiceOperation(self.context, self.resource_path, "GetById", [view_id]))
