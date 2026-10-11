from __future__ import annotations

from enum import Enum


class RecipientType(Enum):
    user = "1"
    roleGroup = "2"
    unknownFutureValue = "4"

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.security.RecipientType"
