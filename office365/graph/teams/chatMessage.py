from office365.graph.entity import Entity
from office365.runtime.resource_path import ResourcePath


class ChatMessage(Entity):

    @property
    def replies(self):
        """The collection of replies."""
        if self.is_property_available("replies"):
            return self.properties['replies']
        else:
            from office365.graph.teams.chatMessageCollection import ChatMessageCollection
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
