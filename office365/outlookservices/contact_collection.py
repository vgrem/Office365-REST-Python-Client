from office365.outlookservices.contact import Contact
from office365.runtime.client_object_collection import ClientObjectCollection
from office365.runtime.client_query import ClientQuery
from office365.runtime.resource_path_entry import ResourcePathEntry


class ContactCollection(ClientObjectCollection):
    """User's contact collection"""

    def add_from_json(self, contact_creation_information):
        """Creates a Contact resource from JSON"""
        contact = Contact(self.context)
        qry = ClientQuery.create_entry_query(self, contact_creation_information)
        self.context.add_query(qry, contact)
        self.add_child(contact)
        return contact

    def add(self):
        """Creates a Contact resource"""
        contact = Contact(self.context)
        qry = ClientQuery.create_entry_query(self, contact)
        self.context.add_query(qry, contact)
        self.add_child(contact)
        return contact

    def get_by_id(self, contact_id):
        """Retrieve Contact resource by id"""
        return Contact(self.context,
                       ResourcePathEntry(self.context, self.resource_path, contact_id))
