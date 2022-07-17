from office365.delta_collection import DeltaCollection
from office365.outlook.mail.messages.message import Message


class MessageCollection(DeltaCollection):

    def __init__(self, context, resource_path=None):
        super(MessageCollection, self).__init__(context, Message, resource_path)
