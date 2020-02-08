from office365.runtime.client_object import ClientObject
from office365.runtime.client_query import UpdateEntityQuery, DeleteEntityQuery


class Field(ClientObject):
    """Represents a field in a SharePoint Web site"""

    def update(self):
        """Update the field."""
        qry = UpdateEntityQuery(self)
        self.context.add_query(qry)

    def delete_object(self):
        """Deletes the field."""
        qry = DeleteEntityQuery(self)
        self.context.add_query(qry)
        self.remove_from_parent_collection()
