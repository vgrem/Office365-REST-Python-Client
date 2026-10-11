from __future__ import annotations

from typing import TYPE_CHECKING

from office365.entity import Entity
from office365.entity_collection import EntityCollection
from office365.runtime.paths.resource_path import ResourcePath

if TYPE_CHECKING:
    from office365.communications.max_work_location_details import (
        MaxWorkLocationDetails,
    )
    from office365.directory.users.work_plan_occurrence import WorkPlanOccurrence
    from office365.directory.users.work_plan_recurrence import WorkPlanRecurrence


class WorkHoursAndLocationsSetting(Entity):
    @property
    def max_shared_work_location_details(self) -> MaxWorkLocationDetails:
        """Gets the maxSharedWorkLocationDetails property"""
        from office365.communications.max_work_location_details import (
            MaxWorkLocationDetails,
        )

        return self.properties.get("maxSharedWorkLocationDetails", MaxWorkLocationDetails.unknown)

    @property
    def occurrences(self) -> EntityCollection[WorkPlanOccurrence]:
        """Gets the occurrences property"""
        from office365.directory.users.work_plan_occurrence import WorkPlanOccurrence

        return self.properties.get(
            "occurrences",
            EntityCollection[WorkPlanOccurrence](
                self.context, WorkPlanOccurrence, ResourcePath("occurrences", self.resource_path)
            ),
        )

    @property
    def recurrences(self) -> EntityCollection[WorkPlanRecurrence]:
        """Gets the recurrences property"""
        from office365.directory.users.work_plan_recurrence import WorkPlanRecurrence

        return self.properties.get(
            "recurrences",
            EntityCollection[WorkPlanRecurrence](
                self.context, WorkPlanRecurrence, ResourcePath("recurrences", self.resource_path)
            ),
        )

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.WorkHoursAndLocationsSetting"
