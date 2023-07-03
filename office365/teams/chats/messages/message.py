from office365.entity import Entity
from office365.entity_collection import EntityCollection
from office365.runtime.client_value_collection import ClientValueCollection
from office365.runtime.paths.resource_path import ResourcePath
from office365.teams.chats.messages.attachment import ChatMessageAttachment


class ChatMessage(Entity):
    """
    Represents an individual chat message within a channel or chat.
    The message can be a root message or part of a thread that is defined by the replyToId property in the message.
    """

    @property
    def attachments(self):
        """The collection of replies."""
        return self.properties.get("attachments", ClientValueCollection(ChatMessageAttachment))

    @property
    def replies(self):
        """
        The collection of replies.
        """
        return self.properties.get("replies",
                                   EntityCollection(self.context, ChatMessage,
                                                    ResourcePath("replies", self.resource_path)))

    @property
    def web_url(self):
        """
        Link to the message in Microsoft Teams.

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
