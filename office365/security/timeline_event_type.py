from __future__ import annotations

from enum import Enum


class TimelineEventType(Enum):
    originalDelivery = "0"
    systemTimeTravel = "1"
    dynamicDelivery = "2"
    userUrlClick = "3"
    reprocessed = "4"
    zap = "5"
    quarantineRelease = "6"
    air = "7"
    unknown = "8"
    unknownFutureValue = "127"

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.security.TimelineEventType"
