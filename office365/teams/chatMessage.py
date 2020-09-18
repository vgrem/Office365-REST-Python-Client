from office365.entity import Entity
from office365.runtime.client_value_collection import ClientValueCollection
from office365.runtime.resource_path import ResourcePath
from office365.teams.chatMessageAttachment import ChatMessageAttachment


class ChatMessage(Entity):

    @property
    def attachments(self):
        """The collection of replies."""
        return self.properties.get("attachments", ClientValueCollection(ChatMessageAttachment()))

    @property
    def replies(self):
        """The collection of replies."""
        if self.is_property_available("replies"):
            return self.properties['replies']
        else:
            from office365.teams.chatMessageCollection import ChatMessageCollection
            return ChatMessageCollection(self.context, ResourcePath("replies", self.resource_path))

    @property
    def web_url(self):
        """

        :rtype: str
        """
        return self.properties.get("webUrl", None)

    @property
    def importance(self):
        """
        The importance of the chat message. The possible values are: normal, high, urgent.
        :rtype: str
        """
        return self.properties.get("importance", None)
