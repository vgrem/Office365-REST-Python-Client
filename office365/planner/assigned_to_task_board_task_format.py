from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from office365.entity import Entity

if TYPE_CHECKING:
    from office365.planner.planner_order_hints_by_assignee import (
        PlannerOrderHintsByAssignee,
    )


class PlannerAssignedToTaskBoardTaskFormat(Entity):
    @property
    def order_hints_by_assignee(self) -> PlannerOrderHintsByAssignee:
        """Gets the orderHintsByAssignee property"""
        from office365.planner.planner_order_hints_by_assignee import (
            PlannerOrderHintsByAssignee,
        )

        return self.properties.get("orderHintsByAssignee", PlannerOrderHintsByAssignee())

    @property
    def unassigned_order_hint(self) -> Optional[str]:
        """Gets the unassignedOrderHint property"""
        return self.properties.get("unassignedOrderHint", None)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.PlannerAssignedToTaskBoardTaskFormat"
