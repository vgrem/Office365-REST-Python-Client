from __future__ import annotations

from typing import Optional

from office365.entity import Entity


class SkypeForBusinessUserConversationMember(Entity):
    @property
    def tenant_id(self) -> Optional[str]:
        """Gets the tenantId property"""
        return self.properties.get("tenantId", None)

    @property
    def user_id(self) -> Optional[str]:
        """Gets the userId property"""
        return self.properties.get("userId", None)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.SkypeForBusinessUserConversationMember"
