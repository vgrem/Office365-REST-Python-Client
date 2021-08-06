from office365.entity import Entity
from office365.entity_collection import EntityCollection
from office365.runtime.resource_path import ResourcePath
from office365.teams.messages.chat_message import ChatMessage


class Chat(Entity):
    """A chat is a collection of chatMessages between one or more participants. Participants can be users or apps."""

    @property
    def messages(self):
        """A collection of all the messages in the chat. Nullable."""
        return self.properties.get('messages', EntityCollection(self.context, ChatMessage,
                                                                ResourcePath("messages", self.resource_path)))
