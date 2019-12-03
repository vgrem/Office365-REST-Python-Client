from office365.outlookservices.message import Message
from office365.runtime.client_object_collection import ClientObjectCollection
from office365.runtime.client_query import ClientQuery


class MessageCollection(ClientObjectCollection):
    """Message's collection"""
    def __init__(self, context, resource_path=None):
        super(MessageCollection, self).__init__(context, Message, resource_path)

    def add_from_json(self, message_creation_information):
        """Create a draft of a new message from JSON"""
        contact = Message(self.context)
        qry = ClientQuery.create_entry_query(self, message_creation_information)
        self.context.add_query(qry, contact)
        self.add_child(contact)
        return contact
