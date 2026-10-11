from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from office365.entity import Entity
from office365.entity_collection import EntityCollection
from office365.runtime.client_value_collection import ClientValueCollection
from office365.runtime.paths.resource_path import ResourcePath

if TYPE_CHECKING:
    from office365.directory.extensions.extended_property import (
        MultiValueLegacyExtendedProperty,
        SingleValueLegacyExtendedProperty,
    )
    from office365.directory.extensions.extension import Extension
    from office365.outlook.mail.attachments.attachment import Attachment
    from office365.outlook.mail.item_body import ItemBody
    from office365.outlook.mail.post import Post
    from office365.outlook.mail.recipient import Recipient


class Post(Entity):
    """Represents an individual Post item within a conversationThread entity."""

    @property
    def conversation_id(self) -> Optional[str]:
        """The ID of the conversation the post belongs to."""
        return self.properties.get("conversationId", None)

    @property
    def received_datetime(self) -> datetime:
        """The date and time the post was received."""
        return self.properties.get("receivedDateTime", datetime.min)

    @property
    def body(self) -> ItemBody:
        """Gets the body property"""
        from office365.outlook.mail.item_body import ItemBody

        return self.properties.get("body", ItemBody())

    @property
    def conversation_thread_id(self) -> Optional[str]:
        """Gets the conversationThreadId property"""
        return self.properties.get("conversationThreadId", None)

    @property
    def from_(self) -> Recipient:
        """Gets the from property"""
        from office365.outlook.mail.recipient import Recipient

        return self.properties.get("from", Recipient())

    @property
    def has_attachments(self) -> Optional[bool]:
        """Gets the hasAttachments property"""
        return self.properties.get("hasAttachments", None)

    @property
    def new_participants(self) -> ClientValueCollection[Recipient]:
        """Gets the newParticipants property"""
        from office365.outlook.mail.recipient import Recipient

        return self.properties.get("newParticipants", ClientValueCollection[Recipient](Recipient))

    @property
    def sender(self) -> Recipient:
        """Gets the sender property"""
        from office365.outlook.mail.recipient import Recipient

        return self.properties.get("sender", Recipient())

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
    def in_reply_to(self) -> Post:
        """Gets the inReplyTo property"""
        from office365.outlook.mail.post import Post

        return self.properties.get("inReplyTo", Post(self.context, ResourcePath("inReplyTo", self.resource_path)))

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
        return "microsoft.graph.Post"
