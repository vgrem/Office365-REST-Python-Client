from __future__ import annotations

from typing import Optional

from office365.entity import Entity


class MicrosoftAccountUserConversationMember(Entity):
    @property
    def user_id(self) -> Optional[str]:
        """Gets the userId property"""
        return self.properties.get("userId", None)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.MicrosoftAccountUserConversationMember"
