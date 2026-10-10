from __future__ import annotations

from enum import Enum


class LifecycleTaskCategory(Enum):
    joiner = "1"
    leaver = "2"
    unknownFutureValue = "4"
    mover = "8"

    @property
    def entity_type_name(self):
        return "microsoft.graph.identityGovernance.LifecycleTaskCategory"

    extensibility = "16"
