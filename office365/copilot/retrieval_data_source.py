from __future__ import annotations

from enum import Enum


class RetrievalDataSource(Enum):
    sharePoint = "0"
    oneDriveBusiness = "1"
    externalItem = "2"
    unknownFutureValue = "3"

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.RetrievalDataSource"

    sharePointEmbedded = "4"
