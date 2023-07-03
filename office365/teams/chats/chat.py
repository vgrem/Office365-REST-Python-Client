from office365.entity import Entity
from office365.entity_collection import EntityCollection
from office365.runtime.paths.resource_path import ResourcePath
from office365.teams.apps.installation import TeamsAppInstallation
from office365.teams.chats.messages.message import ChatMessage

from office365.teams.chats.messages.info import ChatMessageInfo
from office365.teams.members.conversation_collection import ConversationMemberCollection
from office365.teams.operations.async_operation import TeamsAsyncOperation
from office365.teams.tabs.tab import TeamsTab


class Chat(Entity):
    """A chat is a collection of chatMessages between one or more participants. Participants can be users or apps."""

    @property
    def topic(self):
        """(Optional) Subject or topic for the chat. Only available for group chats."""
        return self.properties.get("topic", None)

    @property
    def installed_apps(self):
        """A collection of all the apps in the chat. Nullable.
        """
        return self.properties.get('installedApps',
                                   EntityCollection(self.context, TeamsAppInstallation,
                                                    ResourcePath("installedApps", self.resource_path)))

    @property
    def last_message_preview(self):
        """Preview of the last message sent in the chat. Null if no messages have been sent in the chat."""
        return self.properties.get('lastMessagePreview',
                                   ChatMessageInfo(self.context,
                                                   ResourcePath("lastMessagePreview", self.resource_path)))

    @property
    def members(self):
        """A collection of membership records associated with the chat.
        """
        return self.properties.setdefault('members',
                                          ConversationMemberCollection(self.context,
                                                                       ResourcePath("members", self.resource_path)))

    @property
    def messages(self):
        """A collection of all the messages in the chat. Nullable."""
        return self.properties.get('messages', EntityCollection(self.context, ChatMessage,
                                                                ResourcePath("messages", self.resource_path)))

    @property
    def operations(self):
        """
        A collection of all the Teams async operations that ran or are running on the chat. Nullable.
        """
        return self.properties.get('operations',
                                   EntityCollection(self.context, TeamsAsyncOperation,
                                                    ResourcePath("operations", self.resource_path)))

    @property
    def tabs(self):
        """A collection of all the tabs in the chat."""
        return self.properties.get('tabs',
                                   EntityCollection(self.context, TeamsTab, ResourcePath("tabs", self.resource_path)))

    def get_property(self, name, default_value=None):
        if default_value is None:
            property_mapping = {
                "installedApps": self.installed_apps,
                "lastMessagePreview": self.last_message_preview
            }
            default_value = property_mapping.get(name, None)
        return super(Chat, self).get_property(name, default_value)
