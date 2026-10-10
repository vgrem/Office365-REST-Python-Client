from __future__ import annotations

from enum import Enum


class RelationshipStatus(Enum):
    active = "0"
    terminated = "1"
    terminationRequestedByGoverningTenant = "2"
    unknownFutureValue = "3"

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.RelationshipStatus"
