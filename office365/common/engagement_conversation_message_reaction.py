from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from office365.entity import Entity

if TYPE_CHECKING:
    from office365.communications.engagement_identity_set import EngagementIdentitySet
    from office365.teams.viva.engagement.conversationmessagereactiontype import (
        EngagementConversationMessageReactionType,
    )


class EngagementConversationMessageReaction(Entity):
    @property
    def created_date_time(self) -> Optional[datetime]:
        """Gets the createdDateTime property"""
        return self.properties.get("createdDateTime", datetime.min)

    @property
    def reaction_by(self) -> EngagementIdentitySet:
        """Gets the reactionBy property"""
        from office365.communications.engagement_identity_set import (
            EngagementIdentitySet,
        )

        return self.properties.get("reactionBy", EngagementIdentitySet())

    @property
    def reaction_type(self) -> EngagementConversationMessageReactionType:
        """Gets the reactionType property"""
        from office365.teams.viva.engagement.conversationmessagereactiontype import (
            EngagementConversationMessageReactionType,
        )

        return self.properties.get("reactionType", EngagementConversationMessageReactionType.like)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.EngagementConversationMessageReaction"
