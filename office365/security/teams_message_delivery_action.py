from __future__ import annotations

from enum import Enum


class TeamsMessageDeliveryAction(Enum):
    unknown = "0"
    deliveredAsSpam = "1"
    delivered = "2"
    blocked = "3"
    replaced = "4"
    unknownFutureValue = "31"

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.security.TeamsMessageDeliveryAction"
