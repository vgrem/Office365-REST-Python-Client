from __future__ import annotations

from enum import Enum


class OnboardingStatus(Enum):
    insufficientInfo = "0"
    onboarded = "1"
    canBeOnboarded = "2"
    unsupported = "3"
    unknownFutureValue = "31"

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.security.OnboardingStatus"
