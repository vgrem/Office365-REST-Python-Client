from office365.runtime.client_object import ClientObject
from office365.runtime.client_query import DeleteEntityQuery
from office365.runtime.resource_path import ResourcePath
from office365.sharepoint.view_field_collection import ViewFieldCollection


class View(ClientObject):
    """Specifies a list view."""

    @property
    def viewFields(self):
        if self.is_property_available('ViewFields'):
            return self.properties['ViewFields']
        else:
            return ViewFieldCollection(self.context, ResourcePath("ViewFields", self.resourcePath))

    def delete_object(self):
        """The recommended way to delete a view is to send a DELETE request to the View resource endpoint, as shown
        in View request examples."""
        qry = DeleteEntityQuery(self)
        self.context.add_query(qry)
        self.remove_from_parent_collection()
