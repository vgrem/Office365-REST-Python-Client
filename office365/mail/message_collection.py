from office365.entity_collection import EntityCollection
from office365.mail.message import Message


class MessageCollection(EntityCollection):
    """Message's collection"""
    def __init__(self, context, resource_path=None):
        super(MessageCollection, self).__init__(context, Message, resource_path)

    def add(self):
        """
        Use this API to create a draft of a new message. Drafts can be created in any folder
        and optionally updated before sending. To save to the Drafts folder, use the /messages shortcut.

        """
        pass

    def get(self):
        """
        :rtype: MessageCollection
        """
        return super(MessageCollection, self).get()
