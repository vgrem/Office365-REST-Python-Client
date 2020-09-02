from urllib.parse import quote

from office365.graph.entity import Entity
from office365.graph.teams.chatMessageCollection import ChatMessageCollection
from office365.runtime.queries.delete_entity_query import DeleteEntityQuery
from office365.runtime.resource_path import ResourcePath


class Channel(Entity):
    """Teams are made up of channels, which are the conversations you have with your teammates"""

    def delete_object(self):
        """Deletes the channel."""
        qry = DeleteEntityQuery(self)
        self.context.add_query(qry)
        self.remove_from_parent_collection()
        return self

    @property
    def messages(self):
        """A collection of all the messages in the channel. A navigation property. Nullable."""
        if self.is_property_available("messages"):
            return self.properties['messages']
        else:
            return ChatMessageCollection(self.context, ResourcePath("messages", self.resource_path))

    @property
    def web_url(self):
        """A hyperlink that will navigate to the channel in Microsoft Teams. This is the URL that you get when you
        right-click a channel in Microsoft Teams and select Get link to channel. This URL should be treated as an
        opaque blob, and not parsed. Read-only.

        :rtype: str or None """
        return self.properties.get('webUrl', None)

    def set_property(self, name, value, persist_changes=True):
        super(Channel, self).set_property(name, value, persist_changes)
        # fallback: fix resource path
        if name == "id":
            channel_id = quote(value)
            self._resource_path = ResourcePath(channel_id, self.resource_path.parent)
