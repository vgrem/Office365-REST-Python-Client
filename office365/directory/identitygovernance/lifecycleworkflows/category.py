from __future__ import annotations

from enum import Enum


class LifecycleWorkflowCategory(Enum):
    joiner = "0"
    leaver = "1"
    unknownFutureValue = "2"
    mover = "3"

    @property
    def entity_type_name(self):
        return "microsoft.graph.identityGovernance.LifecycleWorkflowCategory"

    extensibility = "4"
