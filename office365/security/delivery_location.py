from __future__ import annotations

from enum import Enum


class DeliveryLocation(Enum):
    unknown = "0"
    inbox_folder = "1"
    junkFolder = "2"
    deletedFolder = "3"
    quarantine = "4"
    onprem_external = "5"
    failed = "6"
    dropped = "7"
    others = "10"
    unknownFutureValue = "127"

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.security.DeliveryLocation"
