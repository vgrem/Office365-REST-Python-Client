from __future__ import annotations

from enum import Enum


class CoachmarkLocationType(Enum):
    unknown = "0"
    fromEmail = "1"
    subject = "2"
    externalTag = "3"
    displayName = "4"
    messageBody = "5"
    unknownFutureValue = "6"

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.CoachmarkLocationType"
