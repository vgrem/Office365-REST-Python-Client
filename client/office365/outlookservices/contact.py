from client.office365.runtime.client_object import ClientObject
from client.office365.runtime.client_query import ClientQuery


class Contact(ClientObject):
    """User's contact."""

    def update(self):
        qry = ClientQuery.update_entry_query(self)
        self.context.add_query(qry)
