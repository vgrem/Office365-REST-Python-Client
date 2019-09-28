from office365.runtime.client_object import ClientObject
from office365.runtime.client_query import ClientQuery


class Field(ClientObject):
    """Represents a field in a SharePoint Web site"""

    def update(self):
        """Update the field."""
        qry = ClientQuery.update_entry_query(self)
        self.context.add_query(qry)

    def delete_object(self):
        """Deletes the field."""
        qry = ClientQuery.delete_entry_query(self)
        self.context.add_query(qry)
        self.remove_from_parent_collection()
