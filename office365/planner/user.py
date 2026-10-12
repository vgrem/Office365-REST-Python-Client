from __future__ import annotations

from typing import TYPE_CHECKING

from office365.entity import Entity
from office365.planner.internal.paths.collections import PlannerCollectionPath

if TYPE_CHECKING:
    from office365.planner.plans.collection import PlannerPlanCollection
    from office365.planner.tasks.collection import PlannerTaskCollection


class PlannerUser(Entity):
    """The plannerUser resource provide access to Planner resources for a user.
    It doesn't contain any usable properties."""

    @property
    def plans(self) -> PlannerPlanCollection:
        """Returns the plannerTasks assigned to the user."""
        from office365.planner.plans.collection import PlannerPlanCollection

        return self.properties.get(
            "plans", PlannerPlanCollection(self.context, PlannerCollectionPath("plans", self.resource_path))
        )

    @property
    def tasks(self) -> PlannerTaskCollection:
        """Returns the plannerTasks assigned to the user."""
        from office365.planner.tasks.collection import PlannerTaskCollection

        return self.properties.get(
            "tasks",
            PlannerTaskCollection(self.context, parent=self),
        )

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.PlannerUser"
