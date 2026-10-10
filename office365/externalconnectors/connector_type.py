from __future__ import annotations

from enum import Enum


class ConnectorType(Enum):
    sapIag = "0"
    unknownFutureValue = "3"

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.ConnectorType"
