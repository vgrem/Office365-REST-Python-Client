from __future__ import annotations

from enum import Enum


class AccessReviewReviewerScopeType(Enum):
    user = "0"
    group = "1"
    self = "2"
    manager = "3"
    sponsor = "4"
    resourceOwner = "5"
    managerOrSponsor = "6"
    unknownFutureValue = "7"

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.AccessReviewReviewerScopeType"
