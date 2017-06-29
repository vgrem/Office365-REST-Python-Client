from office365.runtime.client_object import ClientObject
from office365.runtime.client_query import ClientQuery


class View(ClientObject):
    """Specifies a list view."""

    def delete_object(self):
        """The recommended way to delete a view is to send a DELETE request to the View resource endpoint, as shown
        in View request examples."""
        qry = ClientQuery.delete_entry_query(self)
        self.context.add_query(qry)
        self.remove_from_parent_collection()
