from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from office365.entity import Entity
from office365.entity_collection import EntityCollection
from office365.runtime.paths.resource_path import ResourcePath
from office365.teams.viva.engagement.creationmode import EngagementCreationMode

if TYPE_CHECKING:
    from office365.teams.viva.engagement.conversation_message import (
        EngagementConversationMessage,
    )


class EngagementConversation(Entity):
    @property
    def creation_mode(self) -> EngagementCreationMode:
        """Gets the creationMode property"""
        return self.properties.get("creationMode", EngagementCreationMode.none)

    @property
    def starter_id(self) -> Optional[str]:
        """Gets the starterId property"""
        return self.properties.get("starterId", None)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.EngagementConversation"

    @property
    def messages(self) -> EntityCollection[EngagementConversationMessage]:
        """Gets the messages property"""
        from office365.teams.viva.engagement.conversation_message import (
            EngagementConversationMessage,
        )

        return self.properties.get(
            "messages",
            EntityCollection[EngagementConversationMessage](
                self.context, EngagementConversationMessage, ResourcePath("messages", self.resource_path)
            ),
        )

    @property
    def starter(self) -> EngagementConversationMessage:
        """Gets the starter property"""
        from office365.teams.viva.engagement.conversation_message import (
            EngagementConversationMessage,
        )

        return self.properties.get(
            "starter", EngagementConversationMessage(self.context, ResourcePath("starter", self.resource_path))
        )
