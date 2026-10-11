from __future__ import annotations

from typing import Optional

from office365.entity import Entity


class AnonymousGuestConversationMember(Entity):
    @property
    def anonymous_guest_id(self) -> Optional[str]:
        """Gets the anonymousGuestId property"""
        return self.properties.get("anonymousGuestId", None)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.AnonymousGuestConversationMember"
