from __future__ import annotations

from datetime import datetime
from typing import Optional

from office365.entity import Entity
from office365.runtime.types.collections import StringCollection


class ConversationMember(Entity):
    """Represents a user in a team, a channel, or a chat. See also aadUserConversationMember."""

    def __str__(self) -> str:
        return self.display_name or self.entity_type_name

    @property
    def display_name(self) -> str | None:
        """The display name of the user."""
        return self.properties.get("displayName")

    @property
    def roles(self) -> StringCollection:
        """The roles for that user."""
        return self.properties.setdefault("roles", StringCollection())

    @property
    def visible_history_start_date_time(self) -> Optional[datetime]:
        """Gets the visibleHistoryStartDateTime property"""
        return self.properties.get("visibleHistoryStartDateTime", datetime.min)

    @property
    def entity_type_name(self) -> str:
        # Graph rejects the abstract ``conversationMember`` type on writes and
        # expects the concrete AAD user type (Teams members are always AAD users).
        # The claim is therefore shared with ``aad_user_conversation.py``, which is
        # deliberate: the generator reports both claimants, and every Teams member
        # is an AAD user, so either class produces the same ``@odata.type``.
        return "microsoft.graph.AadUserConversationMember"
