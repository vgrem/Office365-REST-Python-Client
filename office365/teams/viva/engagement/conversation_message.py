from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from office365.entity import Entity
from office365.entity_collection import EntityCollection
from office365.runtime.paths.resource_path import ResourcePath

if TYPE_CHECKING:
    from office365.communications.engagement_identity_set import EngagementIdentitySet
    from office365.outlook.mail.item_body import ItemBody
    from office365.teams.viva.engagement.conversation import EngagementConversation
    from office365.teams.viva.engagement.conversation_message import (
        EngagementConversationMessage,
    )
    from office365.teams.viva.engagement.conversation_message_reaction import (
        EngagementConversationMessageReaction,
    )
    from office365.teams.viva.engagement.creationmode import EngagementCreationMode


class EngagementConversationMessage(Entity):
    @property
    def body(self) -> ItemBody:
        """Gets the body property"""
        from office365.outlook.mail.item_body import ItemBody

        return self.properties.get("body", ItemBody())

    @property
    def created_date_time(self) -> Optional[datetime]:
        """Gets the createdDateTime property"""
        return self.properties.get("createdDateTime", datetime.min)

    @property
    def creation_mode(self) -> EngagementCreationMode:
        """Gets the creationMode property"""
        from office365.teams.viva.engagement.creationmode import EngagementCreationMode

        return self.properties.get("creationMode", EngagementCreationMode.none)

    @property
    def from_(self) -> EngagementIdentitySet:
        """Gets the from property"""
        from office365.communications.engagement_identity_set import (
            EngagementIdentitySet,
        )

        return self.properties.get("from", EngagementIdentitySet())

    @property
    def last_modified_date_time(self) -> Optional[datetime]:
        """Gets the lastModifiedDateTime property"""
        return self.properties.get("lastModifiedDateTime", datetime.min)

    @property
    def reply_to_id(self) -> Optional[str]:
        """Gets the replyToId property"""
        return self.properties.get("replyToId", None)

    @property
    def conversation(self) -> EngagementConversation:
        """Gets the conversation property"""
        from office365.teams.viva.engagement.conversation import EngagementConversation

        return self.properties.get(
            "conversation", EngagementConversation(self.context, ResourcePath("conversation", self.resource_path))
        )

    @property
    def reactions(self) -> EntityCollection[EngagementConversationMessageReaction]:
        """Gets the reactions property"""
        from office365.teams.viva.engagement.conversation_message_reaction import (
            EngagementConversationMessageReaction,
        )

        return self.properties.get(
            "reactions",
            EntityCollection[EngagementConversationMessageReaction](
                self.context, EngagementConversationMessageReaction, ResourcePath("reactions", self.resource_path)
            ),
        )

    @property
    def replies(self) -> EntityCollection[EngagementConversationMessage]:
        """Gets the replies property"""
        from office365.teams.viva.engagement.conversation_message import (
            EngagementConversationMessage,
        )

        return self.properties.get(
            "replies",
            EntityCollection[EngagementConversationMessage](
                self.context, EngagementConversationMessage, ResourcePath("replies", self.resource_path)
            ),
        )

    @property
    def reply_to(self) -> EngagementConversationMessage:
        """Gets the replyTo property"""
        from office365.teams.viva.engagement.conversation_message import (
            EngagementConversationMessage,
        )

        return self.properties.get(
            "replyTo", EngagementConversationMessage(self.context, ResourcePath("replyTo", self.resource_path))
        )

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.EngagementConversationMessage"
