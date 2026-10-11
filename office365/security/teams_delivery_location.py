from __future__ import annotations

from enum import Enum


class TeamsDeliveryLocation(Enum):
    unknown = "0"
    teams = "1"
    quarantine = "2"
    failed = "3"
    unknownFutureValue = "31"

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.security.TeamsDeliveryLocation"
