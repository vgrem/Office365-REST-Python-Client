from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from office365.entity import Entity
from office365.entity_collection import EntityCollection
from office365.runtime.paths.resource_path import ResourcePath

if TYPE_CHECKING:
    from office365.directory.extensions.extended_property import (
        MultiValueLegacyExtendedProperty,
        SingleValueLegacyExtendedProperty,
    )
    from office365.directory.extensions.extension import Extension
    from office365.outlook.mail.attachments.attachment import Attachment
    from office365.outlook.mail.item_body import ItemBody


class Note(Entity):
    @property
    def body(self) -> ItemBody:
        """Gets the body property"""
        from office365.outlook.mail.item_body import ItemBody

        return self.properties.get("body", ItemBody())

    @property
    def body_preview(self) -> Optional[str]:
        """Gets the bodyPreview property"""
        return self.properties.get("bodyPreview", None)

    @property
    def has_attachments(self) -> Optional[bool]:
        """Gets the hasAttachments property"""
        return self.properties.get("hasAttachments", None)

    @property
    def is_deleted(self) -> Optional[bool]:
        """Gets the isDeleted property"""
        return self.properties.get("isDeleted", None)

    @property
    def subject(self) -> Optional[str]:
        """Gets the subject property"""
        return self.properties.get("subject", None)

    @property
    def attachments(self) -> EntityCollection[Attachment]:
        """Gets the attachments property"""
        from office365.outlook.mail.attachments.attachment import Attachment

        return self.properties.get(
            "attachments",
            EntityCollection[Attachment](self.context, Attachment, ResourcePath("attachments", self.resource_path)),
        )

    @property
    def extensions(self) -> EntityCollection[Extension]:
        """Gets the extensions property"""
        from office365.directory.extensions.extension import Extension

        return self.properties.get(
            "extensions",
            EntityCollection[Extension](self.context, Extension, ResourcePath("extensions", self.resource_path)),
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
        return "microsoft.graph.Note"
