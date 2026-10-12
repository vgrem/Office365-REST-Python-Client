from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from office365.planner.entity import PlannerEntity

if TYPE_CHECKING:
    from office365.planner.tasks.collection import PlannerTaskCollection


class PlannerBucket(PlannerEntity):
    """Represents a bucket (or "custom column") for tasks in a plan in Microsoft 365.
    It is contained in a plannerPlan and can have a collection of plannerTasks.
    """

    @property
    def name(self) -> Optional[str]:
        """Required. Name of the bucket."""
        return self.properties.get("name", None)

    @name.setter
    def name(self, value: str):
        self.set_property("name", value)

    @property
    def plan_id(self) -> Optional[str]:
        """Required. Name of the bucket."""
        return self.properties.get("planId", None)

    @plan_id.setter
    def plan_id(self, value: str):
        self.set_property("planId", value)

    @property
    def tasks(self) -> PlannerTaskCollection:
        """Read-only. Nullable. Collection of tasks in the bucket."""
        from office365.planner.tasks.collection import PlannerTaskCollection

        return self.properties.get(
            "tasks",
            PlannerTaskCollection(self.context, parent=self),
        )

    @property
    def order_hint(self) -> Optional[str]:
        """Gets the orderHint property"""
        return self.properties.get("orderHint", None)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.PlannerBucket"
