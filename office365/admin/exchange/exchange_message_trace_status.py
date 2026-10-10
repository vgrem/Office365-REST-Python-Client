from __future__ import annotations

from enum import Enum


class ExchangeMessageTraceStatus(Enum):
    gettingStatus = "1"
    pending = "2"
    failed = "3"
    delivered = "4"
    expanded = "5"
    quarantined = "6"
    filteredAsSpam = "7"
    unknownFutureValue = "8"

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.ExchangeMessageTraceStatus"

    recalled = "9"
