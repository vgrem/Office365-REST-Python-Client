from office365.entity import Entity
from office365.entity_collection import EntityCollection
from office365.outlook.mail.conversation_thread import ConversationThread
from office365.runtime.paths.resource_path import ResourcePath


class Conversation(Entity):
    """
    A conversation is a collection of threads, and a thread contains posts to that thread.
    All threads and posts in a conversation share the same subject.
    """

    @property
    def threads(self):
        """A collection of all the conversation threads in the conversation."""
        return self.properties.get('threads',
                                   EntityCollection(self.context, ConversationThread,
                                                    ResourcePath("threads", self.resource_path)))
