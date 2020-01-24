from office365.outlookservices.contact import Contact
from office365.runtime.client_object_collection import ClientObjectCollection
from office365.runtime.client_query import CreateEntityQuery
from office365.runtime.resource_path_entity import ResourcePathEntity


class ContactCollection(ClientObjectCollection):
    """User's contact collection"""

    def __init__(self, context, resource_path=None):
        super(ContactCollection, self).__init__(context, Contact, resource_path)

    def add_from_json(self, contact_creation_information):
        """Creates a Contact resource from JSON"""
        contact = Contact(self.context)
        qry = CreateEntityQuery(self, contact_creation_information)
        self.context.add_query(qry, contact)
        self.add_child(contact)
        return contact

    def add(self):
        """Creates a Contact resource"""
        contact = Contact(self.context)
        qry = CreateEntityQuery(self, contact)
        self.context.add_query(qry, contact)
        self.add_child(contact)
        return contact

    def get_by_id(self, contact_id):
        """Retrieve Contact resource by id"""
        return Contact(self.context,
                       ResourcePathEntity(self.context, self.resourcePath, contact_id))
