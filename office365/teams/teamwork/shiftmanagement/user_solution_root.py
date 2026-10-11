from __future__ import annotations

from typing import TYPE_CHECKING

from office365.entity import Entity
from office365.runtime.paths.resource_path import ResourcePath

if TYPE_CHECKING:
    from office365.teams.teamwork.shiftmanagement.working_time_schedule import (
        WorkingTimeSchedule,
    )


class UserSolutionRoot(Entity):
    """Represents an identifier that relates a user to the working time schedule triggers."""

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.UserSolutionRoot"

    @property
    def working_time_schedule(self) -> WorkingTimeSchedule:
        """Gets the workingTimeSchedule property"""
        from office365.teams.teamwork.shiftmanagement.working_time_schedule import (
            WorkingTimeSchedule,
        )

        return self.properties.get(
            "workingTimeSchedule",
            WorkingTimeSchedule(self.context, ResourcePath("workingTimeSchedule", self.resource_path)),
        )
