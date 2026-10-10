from __future__ import annotations

from enum import Enum


class AccessReviewInstanceDecisionItemApplyResult(Enum):
    new = "0"
    appliedSuccessfully = "1"
    appliedWithUnknownFailure = "2"
    appliedSuccessfullyButObjectNotFound = "3"
    applyNotSupported = "4"
    unknownFutureValue = "5"

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.AccessReviewInstanceDecisionItemApplyResult"
