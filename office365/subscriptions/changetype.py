from __future__ import annotations

from enum import Enum


class ChangeType(Enum):
    created = "0"
    updated = "1"
    deleted = "2"

    @property
    def entity_type_name(self):
        return "microsoft.graph.ChangeType"

    unknownFutureValue = "3"
