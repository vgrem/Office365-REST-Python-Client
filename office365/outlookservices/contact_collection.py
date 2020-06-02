from office365.outlookservices.contact import Contact
from office365.runtime.client_object_collection import ClientObjectCollection
from office365.runtime.client_query import CreateEntityQuery
from office365.runtime.resource_path import ResourcePath


class ContactCollection(ClientObjectCollection):
    """User's contact collection"""

    def __init__(self, context, resource_path=None):
        super(ContactCollection, self).__init__(context, Contact, resource_path)

    def add_from_json(self, contact_creation_information):
        """Creates a Contact resource from JSON"""
        contact = Contact(self.context)
        self.add_child(contact)
        qry = CreateEntityQuery(self, contact_creation_information, contact)
        self.context.add_query(qry)
        return contact

    def add(self):
        """Creates a Contact resource"""
        contact = Contact(self.context)
        self.add_child(contact)
        qry = CreateEntityQuery(self, contact, contact)
        self.context.add_query(qry)
        return contact

    def get_by_id(self, contact_id):
        """Retrieve Contact resource by id"""
        return Contact(self.context,
                       ResourcePath(contact_id, self.resource_path))
