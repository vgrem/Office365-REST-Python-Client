from office365.runtime.client_object_collection import ClientObjectCollection
from office365.sharepoint.view import View


class ViewCollection(ClientObjectCollection):
    """Represents a collection of View resources."""

    def get_by_title(self, view_title):
        """Gets the list view with the specified title."""
        resourcePath = self.resource_path + "/getbytitle('{0}')".format(view_title)
        view = View(self.context, resourcePath)
        return view

    def get_by_id(self, view_id):
        """Gets the list view with the specified ID."""
        resourcePath = self.resource_path + "/getbyid('{0}')".format(view_id)
        view = View(self.context, resourcePath)
        return view
