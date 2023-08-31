from office365.directory.extensions.extended_property import SingleValueLegacyExtendedProperty, \
    MultiValueLegacyExtendedProperty
from office365.entity import Entity
from office365.entity_collection import EntityCollection
from office365.outlook.mail.messages.collection import MessageCollection
from office365.outlook.mail.messages.rules.rule import MessageRule
from office365.runtime.paths.resource_path import ResourcePath
from office365.runtime.queries.service_operation import ServiceOperationQuery


class MailFolder(Entity):
    """A mail folder in a user's mailbox, such as Inbox and Drafts. Mail folders can contain messages,
    other Outlook items, and child mail folders."""

    def copy(self, destination_id):
        """
        Copy a mailfolder and its contents to another mailfolder.
        :param str destination_id: The folder ID, or a well-known folder name. For a list of supported well-known folder
            names, see mailFolder resource type.
        """
        return_type = MailFolder(self.context)
        payload = {"DestinationId": destination_id}
        qry = ServiceOperationQuery(self, "copy", None, payload, None, return_type)
        self.context.add_query(qry)
        return return_type

    @property
    def child_folder_count(self):
        """
        The number of immediate child mailFolders in the current mailFolder.
        :rtype: int or None
        """
        return self.properties.get("childFolderCount", None)

    @property
    def display_name(self):
        """
        The name of the Mail folder
        :rtype: str or None
        """
        return self.properties.get("displayName", None)

    @property
    def is_hidden(self):
        """
        Indicates whether the mailFolder is hidden. This property can be set only when creating the folder.
        Find more information in Hidden mail folders.
        :rtype: bool or None
        """
        return self.properties.get("isHidden", None)

    @property
    def parent_folder_id(self):
        """
        The unique identifier for the mailFolder's parent mailFolder.
        :rtype: str or None
        """
        return self.properties.get('parentFolderId', None)

    @property
    def total_item_count(self):
        """
        The number of items in the mailFolder.
        :rtype: int
        """
        return self.properties.get("totalItemCount", None)

    @property
    def unread_item_count(self):
        """
        The number of items in the mailFolder marked as unread.
        :rtype: int
        """
        return self.properties.get("unreadItemCount", None)

    @property
    def child_folders(self):
        """The collection of child folders in the mailFolder. """
        return self.properties.get('childFolders',
                                   EntityCollection(self.context, MailFolder,
                                                    ResourcePath("childFolders", self.resource_path)))

    @property
    def message_rules(self):
        """"""
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
