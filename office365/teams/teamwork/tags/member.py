from __future__ import annotations

from typing import Optional

from office365.entity import Entity


class TeamworkTagMember(Entity):
    """Represents a user in a team to whom a tag is applied."""

    def __str__(self):
        return self.display_name or self.entity_type_name

    @property
    def display_name(self) -> Optional[str]:
        """The member's display name."""
        return self.properties.get("displayName", None)

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
        return "microsoft.graph.TeamworkTagMember"
