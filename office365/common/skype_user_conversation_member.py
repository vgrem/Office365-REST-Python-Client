from __future__ import annotations

from typing import Optional

from office365.entity import Entity


class SkypeUserConversationMember(Entity):
    @property
    def skype_id(self) -> Optional[str]:
        """Gets the skypeId property"""
        return self.properties.get("skypeId", None)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.SkypeUserConversationMember"
