from __future__ import annotations

from typing import Optional

from office365.entity import Entity


class PhoneUserConversationMember(Entity):
    @property
    def phone_number(self) -> Optional[str]:
        """Gets the phoneNumber property"""
        return self.properties.get("phoneNumber", None)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.PhoneUserConversationMember"
