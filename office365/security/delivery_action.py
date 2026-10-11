from __future__ import annotations

from enum import Enum


class DeliveryAction(Enum):
    unknown = "0"
    deliveredToJunk = "1"
    delivered = "2"
    blocked = "3"
    replaced = "4"
    unknownFutureValue = "127"

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.security.DeliveryAction"
