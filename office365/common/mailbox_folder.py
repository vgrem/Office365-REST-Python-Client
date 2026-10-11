from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from office365.entity import Entity
from office365.entity_collection import EntityCollection
from office365.runtime.paths.resource_path import ResourcePath

if TYPE_CHECKING:
    from office365.common.mailbox_folder import MailboxFolder
    from office365.common.mailbox_item import MailboxItem
    from office365.directory.extensions.extended_property import (
        MultiValueLegacyExtendedProperty,
        SingleValueLegacyExtendedProperty,
    )


class MailboxFolder(Entity):
    @property
    def child_folder_count(self) -> Optional[int]:
        """Gets the childFolderCount property"""
        return self.properties.get("childFolderCount", None)

    @property
    def display_name(self) -> Optional[str]:
        """Gets the displayName property"""
        return self.properties.get("displayName", None)

    @property
    def parent_folder_id(self) -> Optional[str]:
        """Gets the parentFolderId property"""
        return self.properties.get("parentFolderId", None)

    @property
    def total_item_count(self) -> Optional[int]:
        """Gets the totalItemCount property"""
        return self.properties.get("totalItemCount", None)

    @property
    def type(self) -> Optional[str]:
        """Gets the type property"""
        return self.properties.get("type", None)

    @property
    def well_known_name(self) -> Optional[str]:
        """Gets the wellKnownName property"""
        return self.properties.get("wellKnownName", None)

    @property
    def child_folders(self) -> EntityCollection[MailboxFolder]:
        """Gets the childFolders property"""
        from office365.common.mailbox_folder import MailboxFolder

        return self.properties.get(
            "childFolders",
            EntityCollection[MailboxFolder](
                self.context, MailboxFolder, ResourcePath("childFolders", self.resource_path)
            ),
        )

    @property
    def items(self) -> EntityCollection[MailboxItem]:
        """Gets the items property"""
        from office365.common.mailbox_item import MailboxItem

        return self.properties.get(
            "items", EntityCollection[MailboxItem](self.context, MailboxItem, ResourcePath("items", self.resource_path))
        )

    @property
    def multi_value_extended_properties(self) -> EntityCollection[MultiValueLegacyExtendedProperty]:
        """Gets the multiValueExtendedProperties property"""
        from office365.directory.extensions.extended_property import (
            MultiValueLegacyExtendedProperty,
        )

        return self.properties.get(
            "multiValueExtendedProperties",
            EntityCollection[MultiValueLegacyExtendedProperty](
                self.context,
                MultiValueLegacyExtendedProperty,
                ResourcePath("multiValueExtendedProperties", self.resource_path),
            ),
        )

    @property
    def single_value_extended_properties(self) -> EntityCollection[SingleValueLegacyExtendedProperty]:
        """Gets the singleValueExtendedProperties property"""
        from office365.directory.extensions.extended_property import (
            SingleValueLegacyExtendedProperty,
        )

        return self.properties.get(
            "singleValueExtendedProperties",
            EntityCollection[SingleValueLegacyExtendedProperty](
                self.context,
                SingleValueLegacyExtendedProperty,
                ResourcePath("singleValueExtendedProperties", self.resource_path),
            ),
        )

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.MailboxFolder"
