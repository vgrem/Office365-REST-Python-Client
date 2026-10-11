from __future__ import annotations

from dataclasses import dataclass, field

from office365.intune.devices.management.userexperienceanalytics.insightseverity import (
    UserExperienceAnalyticsInsightSeverity,
)
from office365.intune.devices.management.userexperienceanalytics.user_experience_analytics_insight_value import (
    UserExperienceAnalyticsInsightValue,
)
from office365.runtime.client_value import ClientValue
from office365.runtime.client_value_collection import ClientValueCollection


@dataclass
class UserExperienceAnalyticsInsight(ClientValue):
    insightId: str | None = None
    severity: UserExperienceAnalyticsInsightSeverity = UserExperienceAnalyticsInsightSeverity.none
    userExperienceAnalyticsMetricId: str | None = None
    values: ClientValueCollection[UserExperienceAnalyticsInsightValue] = field(
        default_factory=lambda: ClientValueCollection(UserExperienceAnalyticsInsightValue)
    )

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.UserExperienceAnalyticsInsight"
