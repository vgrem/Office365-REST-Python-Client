from __future__ import annotations

from enum import Enum


class SubjectType(Enum):
    user = "1"
    unknownFutureValue = "8"
    provisioningObject = "16"

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.identityGovernance.SubjectType"
