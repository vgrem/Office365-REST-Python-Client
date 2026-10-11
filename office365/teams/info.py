from __future__ import annotations

from typing import Optional

from office365.entity import Entity
from office365.runtime.paths.resource_path import ResourcePath


class TeamInfo(Entity):
    """Represents a team with basic information."""

    def __str__(self):
        return self.display_name or self.entity_type_name

    @property
    def display_name(self) -> Optional[str]:
        """The name of the team."""
        return self.properties.get("displayName", None)

    @property
    def team(self):
        from office365.teams.team import Team

        return self.properties.get("team", Team(self.context, ResourcePath("team", self.resource_path)))

    @property
    def tenant_id(self) -> Optional[str]:
        """Gets the tenantId property"""
        return self.properties.get("tenantId", None)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.TeamInfo"
