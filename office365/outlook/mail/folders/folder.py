from office365.directory.extensions.extended_property import SingleValueLegacyExtendedProperty, \
    MultiValueLegacyExtendedProperty
from office365.entity import Entity
from office365.entity_collection import EntityCollection
from office365.outlook.mail.messages.collection import MessageCollection
from office365.outlook.mail.messages.rules.rule import MessageRule
from office365.runtime.paths.resource_path import ResourcePath


class MailFolder(Entity):
    """A mail folder in a user's mailbox, such as Inbox and Drafts. Mail folders can contain messages,
    other Outlook items, and child mail folders."""

    @property
    def display_name(self):
        """
        The name of the Mail folder

        :rtype: str or None
        """
        return self.properties.get("displayName", None)

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
        return self.properties.get('messages',
                                   MessageCollection(self.context, ResourcePath("messages", self.resource_path)))

    @property
    def multi_value_extended_properties(self):
        """The collection of multi-value extended properties defined for the MailFolder.
        """
        return self.properties.get('multiValueExtendedProperties',
                                   EntityCollection(self.context, MultiValueLegacyExtendedProperty,
                                                    ResourcePath("multiValueExtendedProperties", self.resource_path)))

    @property
    def single_value_extended_properties(self):
        """The collection of single-value extended properties defined for the MailFolder.
        """
        return self.properties.get('singleValueExtendedProperties',
                                   EntityCollection(self.context, SingleValueLegacyExtendedProperty,
                                                    ResourcePath("singleValueExtendedProperties", self.resource_path)))

    def get_property(self, name, default_value=None):
        if default_value is None:
            property_mapping = {
                "childFolders": self.child_folders,
                "messageRules": self.message_rules,
                "multiValueExtendedProperties": self.multi_value_extended_properties,
                "singleValueExtendedProperties": self.single_value_extended_properties
            }
            default_value = property_mapping.get(name, None)
        return super(MailFolder, self).get_property(name, default_value)
