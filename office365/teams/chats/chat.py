from office365.entity import Entity
from office365.entity_collection import EntityCollection
from office365.runtime.paths.resource_path import ResourcePath
from office365.teams.apps.installation import TeamsAppInstallation
from office365.teams.members.conversation import ConversationMember
from office365.teams.chats.message import ChatMessage
from office365.teams.operations.async_operation import TeamsAsyncOperation


class Chat(Entity):
    """A chat is a collection of chatMessages between one or more participants. Participants can be users or apps."""

    @property
    def topic(self):
        """(Optional) Subject or topic for the chat. Only available for group chats."""
        return self.properties.get("topic", None)

    @property
    def installed_apps(self):
        """A collection of all the apps in the chat. Nullable.

        :rtype: EntityCollection
        """
        return self.get_property('installedApps',
                                 EntityCollection(self.context, TeamsAppInstallation,
                                                  ResourcePath("installedApps", self.resource_path)))

    @property
    def members(self):
        """A collection of membership records associated with the chat.

        :rtype: EntityCollection
        """
        return self.properties.get('members',
                                   EntityCollection(self.context, ConversationMember,
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

    def get_property(self, name, default_value=None):
        if default_value is None:
            property_mapping = {
                "installedApps": self.installed_apps
            }
            default_value = property_mapping.get(name, None)
        return super(Chat, self).get_property(name, default_value)
