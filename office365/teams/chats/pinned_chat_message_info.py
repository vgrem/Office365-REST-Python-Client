from __future__ import annotations

from typing import TYPE_CHECKING

from office365.entity import Entity
from office365.runtime.paths.resource_path import ResourcePath

if TYPE_CHECKING:
    from office365.teams.chats.messages.message import ChatMessage


class PinnedChatMessageInfo(Entity):
    @property
    def message(self) -> ChatMessage:
        """Gets the message property"""
        from office365.teams.chats.messages.message import ChatMessage

        return self.properties.get("message", ChatMessage(self.context, ResourcePath("message", self.resource_path)))

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.PinnedChatMessageInfo"
