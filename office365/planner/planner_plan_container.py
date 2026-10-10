from __future__ import annotations

from dataclasses import dataclass

from office365.planner.plans.containertype import PlannerContainerType
from office365.runtime.client_value import ClientValue


@dataclass
class PlannerPlanContainer(ClientValue):
    containerId: str | None = None

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.PlannerPlanContainer"

    type: PlannerContainerType = PlannerContainerType.group

    url: str | None = None
