from __future__ import annotations

from enum import Enum


class RoleType(Enum):
    active = "0"
    eligible = "1"
    application = "2"
    delegated = "3"
    unknownFutureValue = "99"

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.RoleType"
