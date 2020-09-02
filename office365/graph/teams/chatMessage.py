from office365.graph.entity import Entity


class ChatMessage(Entity):

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

