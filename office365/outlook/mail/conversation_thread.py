from office365.entity import Entity
from office365.entity_collection import EntityCollection
from office365.outlook.mail.post import Post
from office365.runtime.paths.resource_path import ResourcePath


class ConversationThread(Entity):
    """A conversationThread is a collection of posts."""

    @property
    def posts(self):
        return self.properties.get('posts',
                                   EntityCollection(self.context, Post, ResourcePath("posts", self.resource_path)))
