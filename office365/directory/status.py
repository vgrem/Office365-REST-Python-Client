from __future__ import annotations

from enum import Enum


class Status(Enum):
    active = "0"
    updated = "1"
    deleted = "2"
    ignored = "3"
    unknownFutureValue = "4"

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.Status"
