from __future__ import annotations

from enum import Enum


class AccountTargetContentType(Enum):
    unknown = "0"
    includeAll = "1"
    addressBook = "2"
    unknownFutureValue = "3"

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.AccountTargetContentType"
