from __future__ import annotations

from typing import TYPE_CHECKING

from office365.entity import Entity
from office365.entity_collection import EntityCollection
from office365.runtime.paths.resource_path import ResourcePath

if TYPE_CHECKING:
    from office365.teams.administration.policy_user_assignment import (
        TeamsPolicyUserAssignment,
    )


class TeamsPolicyAssignment(Entity):
    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.teamsAdministration.TeamsPolicyAssignment"

    @property
    def user_assignments(self) -> EntityCollection[TeamsPolicyUserAssignment]:
        """Gets the userAssignments property"""
        from office365.teams.administration.policy_user_assignment import (
            TeamsPolicyUserAssignment,
        )

        return self.properties.get(
            "userAssignments",
            EntityCollection[TeamsPolicyUserAssignment](
                self.context, TeamsPolicyUserAssignment, ResourcePath("userAssignments", self.resource_path)
            ),
        )
