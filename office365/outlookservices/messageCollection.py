from office365.outlookservices.message import Message
from office365.runtime.client_object_collection import ClientObjectCollection
from office365.runtime.client_query import CreateEntityQuery


class MessageCollection(ClientObjectCollection):
    """Message's collection"""
    def __init__(self, context, resource_path=None):
        super(MessageCollection, self).__init__(context, Message, resource_path)

    def add_from_json(self, message_creation_information):
        """Create a draft of a new message from JSON"""
        contact = Message(self.context)
        self.add_child(contact)
        qry = CreateEntityQuery(self, message_creation_information, contact)
        self.context.add_query(qry)
        return contact
