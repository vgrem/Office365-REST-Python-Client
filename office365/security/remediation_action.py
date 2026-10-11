from __future__ import annotations

from enum import Enum


class RemediationAction(Enum):
    moveToJunk = "1"
    moveToInbox = "2"
    hardDelete = "5"
    softDelete = "6"
    moveToDeletedItems = "7"
    unknownFutureValue = "14"
    moveToQuarantine = "15"

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.security.RemediationAction"
