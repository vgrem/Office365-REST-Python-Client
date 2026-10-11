from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from typing_extensions import Self

if TYPE_CHECKING:
    from office365.outlook.mail.folders.collection import MailFolderCollection

from office365.directory.extensions.extended_property import (
    MultiValueLegacyExtendedProperty,
    SingleValueLegacyExtendedProperty,
)
from office365.directory.permissions.require_permission import require_permission
from office365.entity import Entity
from office365.entity_collection import EntityCollection
from office365.outlook.mail.messages.collection import MessageCollection
from office365.outlook.mail.messages.rules.collection import MessageRuleCollection
from office365.runtime.paths.resource_path import ResourcePath
from office365.runtime.queries.service_operation import ServiceOperationQuery
from office365.runtime.types.odata_property import odata


class MailFolder(Entity):
    """A mail folder in a user's mailbox, such as Inbox and Drafts. Mail folders can contain messages,
    other Outlook items, and child mail folders."""

    def __str__(self):
        return self.display_name or self.entity_type_name

    @require_permission(delegated=["Mail.ReadWrite"], application=["Mail.ReadWrite"])
    def copy(self, destination_id: str) -> MailFolder:
        """Copy a mailfolder and its contents to another mailfolder.

        Args:
            destination_id (str): The folder ID, or a well-known folder name. For a list of supported well-known folder
              names, see mailFolder resource type.
        """
        return_type = MailFolder(self.context)
        payload = {"DestinationId": destination_id}
        qry = ServiceOperationQuery(self, "copy", None, payload, None, return_type)
        self.context.add_query(qry)
        return return_type

    def empty(self, delete_sub_folders=False):
        """Empties the folder

        Args:
            delete_sub_folders (bool): true to indicate that subfolders should also be deleted; otherwise, false.
        """

        def _empty(col: MessageCollection) -> None:
            if not col.has_next:
                [m.delete_object() for m in col]

        self.messages.get_all(page_loaded=_empty)
        return self

    def mark_all_items_as_read(self) -> Self:
        """Marks all items in folder as read."""

        def _mark_all_items_as_read(col: MessageCollection) -> None:
            [m.set_property("isRead", True).update() for m in col.current_page]

        self.messages.get_all(1, page_loaded=_mark_all_items_as_read)
        return self

    def mark_all_items_as_unread(self) -> Self:
        """Marks all items in folder as unread."""

        def _mark_all_items_as_unread(col: MessageCollection) -> None:
            [m.set_property("isRead", False).update() for m in col.current_page]

        self.messages.get_all(page_loaded=_mark_all_items_as_unread)
        return self

    @require_permission(delegated=["Mail.ReadWrite"], application=["Mail.ReadWrite"])
    def permanent_delete(self) -> Self:
        """Permanently delete a mail folder and remove its items from the user's mailbox."""
        qry = ServiceOperationQuery(self, "permanentDelete")
        self.context.add_query(qry)
        return self

    @property
    def child_folder_count(self) -> Optional[int]:
        """The number of immediate child mailFolders in the current mailFolder."""
        return self.properties.get("childFolderCount", None)

    @property
    def display_name(self) -> Optional[str]:
        """The name of the Mail folder"""
        return self.properties.get("displayName", None)

    @property
    def is_hidden(self) -> Optional[bool]:
        """
        Indicates whether the mailFolder is hidden. This property can be set only when creating the folder.
        Find more information in Hidden mail folders.
        """
        return self.properties.get("isHidden", None)

    @property
    def parent_folder_id(self) -> Optional[str]:
        """The unique identifier for the mailFolder's parent mailFolder."""
        return self.properties.get("parentFolderId", None)

    @property
    def total_item_count(self) -> Optional[int]:
        """The number of items in the mailFolder."""
        return self.properties.get("totalItemCount", None)

    @property
    def unread_item_count(self) -> Optional[int]:
        """The number of items in the mailFolder marked as unread."""
        return self.properties.get("unreadItemCount", None)

    @odata(name="childFolders")
    @property
    def child_folders(self) -> MailFolderCollection:
        """The collection of child folders in the mailFolder."""
        from office365.outlook.mail.folders.collection import MailFolderCollection

        return self.properties.get(
            "childFolders", MailFolderCollection(self.context, ResourcePath("childFolders", self.resource_path))
        )

    @odata(name="messageRules")
    @property
    def message_rules(self) -> MessageRuleCollection:
        """"""
        return self.properties.get(
            "messageRules", MessageRuleCollection(self.context, ResourcePath("messageRules", self.resource_path))
        )

    @property
    def messages(self) -> MessageCollection:
        """The collection of messages in the mailFolder."""
        return self.properties.get(
            "messages", MessageCollection(self.context, ResourcePath("messages", self.resource_path))
        )

    @odata(name="multiValueExtendedProperties")
    @property
    def multi_value_extended_properties(self) -> EntityCollection[MultiValueLegacyExtendedProperty]:
        """The collection of multi-value extended properties defined for the MailFolder."""
        return self.properties.get(
            "multiValueExtendedProperties",
            EntityCollection(
                self.context,
                MultiValueLegacyExtendedProperty,
                ResourcePath("multiValueExtendedProperties", self.resource_path),
            ),
        )

    @odata(name="singleValueExtendedProperties")
    @property
    def single_value_extended_properties(self) -> EntityCollection[SingleValueLegacyExtendedProperty]:
        """The collection of single-value extended properties defined for the MailFolder."""
        return self.properties.get(
            "singleValueExtendedProperties",
            EntityCollection(
                self.context,
                SingleValueLegacyExtendedProperty,
                ResourcePath("singleValueExtendedProperties", self.resource_path),
            ),
        )

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.MailFolder"
