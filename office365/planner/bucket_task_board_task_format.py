from __future__ import annotations

from typing import Optional

from office365.planner.entity import PlannerEntity


class PlannerBucketTaskBoardTaskFormat(PlannerEntity):
    @property
    def order_hint(self) -> Optional[str]:
        """Gets the orderHint property"""
        return self.properties.get("orderHint", None)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.PlannerBucketTaskBoardTaskFormat"
