from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from office365.communications.onlinemeetings.online_meeting import OnlineMeeting
from office365.entity import Entity
from office365.runtime.paths.resource_path import ResourcePath
from office365.teams.viva.engagement.conversationmoderationstate import (
    EngagementConversationModerationState,
)

if TYPE_CHECKING:
    from office365.communications.engagement_identity_set import EngagementIdentitySet


class OnlineMeetingEngagementConversation(Entity):
    @property
    def moderation_state(self) -> EngagementConversationModerationState:
        """Gets the moderationState property"""
        return self.properties.get("moderationState", EngagementConversationModerationState.published)

    @property
    def online_meeting_id(self) -> Optional[str]:
        """Gets the onlineMeetingId property"""
        return self.properties.get("onlineMeetingId", None)

    @property
    def upvote_count(self) -> Optional[int]:
        """Gets the upvoteCount property"""
        return self.properties.get("upvoteCount", None)

    @property
    def online_meeting(self) -> OnlineMeeting:
        """Gets the onlineMeeting property"""
        return self.properties.get(
            "onlineMeeting", OnlineMeeting(self.context, ResourcePath("onlineMeeting", self.resource_path))
        )

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.OnlineMeetingEngagementConversation"

    @property
    def organizer(self) -> EngagementIdentitySet:
        """Gets the organizer property"""
        from office365.communications.engagement_identity_set import (
            EngagementIdentitySet,
        )

        return self.properties.get("organizer", EngagementIdentitySet())
