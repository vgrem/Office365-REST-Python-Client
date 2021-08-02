from office365.entity import Entity
from office365.entity_collection import EntityCollection
from office365.outlook.mail.message_rule import MessageRule
from office365.runtime.resource_path import ResourcePath


class MailFolder(Entity):
    """A mail folder in a user's mailbox, such as Inbox and Drafts. Mail folders can contain messages,
    other Outlook items, and child mail folders."""

    @property
    def total_item_count(self):
        """The number of items in the mailFolder."""
        return self.properties.get("totalItemCount", None)

    @property
    def child_folders(self):
        """The collection of child folders in the mailFolder. """
        return self.properties.get('childFolders',
                                   EntityCollection(self.context, MailFolder,
                                                    ResourcePath("childFolders", self.resource_path)))

    @property
    def message_rules(self):
        return self.properties.get('messageRules',
                                   EntityCollection(self.context, MessageRule,
                                                    ResourcePath("messageRules", self.resource_path)))

    @property
    def messages(self):
        """The collection of messages in the mailFolder."""
        from office365.outlook.mail.message_collection import MessageCollection
        return self.properties.get('messages',
                                   MessageCollection(self.context, ResourcePath("messages", self.resource_path)))
