from office365.entity_collection import EntityCollection
from office365.mail.contact import Contact
from office365.runtime.queries.create_entity_query import CreateEntityQuery
from office365.runtime.resource_path import ResourcePath


class ContactCollection(EntityCollection):
    """User's contact collection"""

    def __init__(self, context, resource_path=None):
        super(ContactCollection, self).__init__(context, Contact, resource_path)

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
