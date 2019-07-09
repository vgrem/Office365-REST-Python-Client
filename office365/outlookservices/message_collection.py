from office365.outlookservices.message import Message
from office365.runtime.client_object_collection import ClientObjectCollection


class MessageCollection(ClientObjectCollection):
    """Message's collection"""

    # The object type this collection holds
    item_type = Message
