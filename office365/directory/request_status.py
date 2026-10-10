from __future__ import annotations

from enum import Enum


class RequestStatus(Enum):
    pending = "0"
    accepted = "1"
    rejected = "2"
    unknownFutureValue = "3"

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.RequestStatus"
