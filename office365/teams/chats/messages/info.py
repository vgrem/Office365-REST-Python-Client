from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from office365.entity import Entity
from office365.outlook.mail.item_body import ItemBody

if TYPE_CHECKING:
    from office365.teams.chats.event_message_detail import EventMessageDetail
    from office365.teams.chats.messages.from_identity_set import (
        ChatMessageFromIdentitySet,
    )
    from office365.teams.chats.messages.type import ChatMessageType


class ChatMessageInfo(Entity):
    """Represents a preview of a chatMessage resource. This object can only be fetched as part of a list of chats."""

    @property
    def body(self) -> ItemBody:
        """
        Body of the chatMessage. This will still contain markers for @mentions and attachments even though the
        object does not return @mentions and attachments.
        """
        return self.properties.get("body", ItemBody())

    @property
    def created_datetime(self) -> datetime:
        """Date time object representing the time at which message was created."""
        return self.properties.get("createdDateTime", datetime.min)

    @property
    def event_detail(self) -> EventMessageDetail:
        """Gets the eventDetail property"""
        from office365.teams.chats.event_message_detail import EventMessageDetail

        return self.properties.get("eventDetail", EventMessageDetail())

    @property
    def from_(self) -> ChatMessageFromIdentitySet:
        """Gets the from property"""
        from office365.teams.chats.messages.from_identity_set import (
            ChatMessageFromIdentitySet,
        )

        return self.properties.get("from", ChatMessageFromIdentitySet())

    @property
    def is_deleted(self) -> Optional[bool]:
        """Gets the isDeleted property"""
        return self.properties.get("isDeleted", None)

    @property
    def message_type(self) -> ChatMessageType:
        """Gets the messageType property"""
        from office365.teams.chats.messages.type import ChatMessageType

        return self.properties.get("messageType", ChatMessageType.message)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.ChatMessageInfo"
