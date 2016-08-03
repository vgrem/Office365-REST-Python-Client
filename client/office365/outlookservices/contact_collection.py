from client.office365.outlookservices.contact import Contact
from client.office365.runtime.client_object_collection import ClientObjectCollection
from client.office365.runtime.client_query import ClientQuery


class ContactCollection(ClientObjectCollection):
    """User's contact collection"""

    def add(self, contact_creation_information):
        """Creates a Contact resource"""
        contact = Contact(self.context)
        qry = ClientQuery.create_entry_query(self, contact_creation_information)
        self.context.add_query(qry, contact)
        self.add_child(contact)
        return contact
