from __future__ import annotations

from enum import Enum


class AccessReviewPrincipalScopeType(Enum):
    allUsers = "0"
    guestUsers = "1"
    inactiveUsers = "2"
    inactiveGuestUsers = "3"
    unknownFutureValue = "4"

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.AccessReviewPrincipalScopeType"
