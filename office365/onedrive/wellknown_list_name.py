from __future__ import annotations

from enum import Enum


class WellknownListName(Enum):
    none = "0"
    defaultList = "1"
    flaggedEmails = "2"
    unknownFutureValue = "3"

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.WellknownListName"
