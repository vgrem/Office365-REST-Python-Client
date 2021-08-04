from office365.entity_collection import EntityCollection
from office365.runtime.compat import quote

from office365.entity import Entity
from office365.onedrive.driveItem import DriveItem
from office365.runtime.resource_path import ResourcePath
from office365.teams.chatMessageCollection import ChatMessageCollection
from office365.teams.teamsTab import TeamsTab


class Channel(Entity):
    """Teams are made up of channels, which are the conversations you have with your teammates"""

    @property
    def filesFolder(self):
        """Get the metadata for the location where the files of a channel are stored."""
        return self.properties.get('filesFolder',
                                   DriveItem(self.context, ResourcePath("filesFolder", self.resource_path)))

    @property
    def tabs(self):
        """A collection of all the tabs in the channel. A navigation property."""
        return self.properties.get('tabs',
                                   EntityCollection(self.context, TeamsTab, ResourcePath("tabs", self.resource_path)))

    @property
    def messages(self):
        """A collection of all the messages in the channel. A navigation property. Nullable."""
        return self.properties.get('messages',
                                   ChatMessageCollection(self.context, ResourcePath("messages", self.resource_path)))

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
