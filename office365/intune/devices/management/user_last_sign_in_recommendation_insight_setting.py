from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from office365.directory.audit.usersigninrecommendationscope import (
    UserSignInRecommendationScope,
)
from office365.runtime.client_value import ClientValue

if TYPE_CHECKING:
    from office365.runtime.types.duration import timedelta


@dataclass
class UserLastSignInRecommendationInsightSetting(ClientValue):
    recommendationLookBackDuration: timedelta | None = None
    signInScope: UserSignInRecommendationScope = UserSignInRecommendationScope.tenant

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.UserLastSignInRecommendationInsightSetting"
