from client.office365.runtime.client_object import ClientObject
from client.office365.runtime.client_query import ClientQuery


class Contact(ClientObject):
    """User's contact."""

    def update(self):
        qry = ClientQuery.update_entry_query(self)
        self.context.add_query(qry)

    def delete_object(self):
        """Deletes the contact."""
        qry = ClientQuery.delete_entry_query(self)
        self.context.add_query(qry)

    @property
    def contact_id(self):
        if self.is_property_available('Id'):
            return self.properties["Id"]
        return None
