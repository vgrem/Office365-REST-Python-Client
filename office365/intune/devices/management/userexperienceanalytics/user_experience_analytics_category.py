from __future__ import annotations

from typing import TYPE_CHECKING

from office365.entity import Entity
from office365.entity_collection import EntityCollection
from office365.runtime.client_value_collection import ClientValueCollection
from office365.runtime.paths.resource_path import ResourcePath

if TYPE_CHECKING:
    from office365.intune.devices.management.userexperienceanalytics.user_experience_analytics_insight import (
        UserExperienceAnalyticsInsight,
    )
    from office365.intune.devices.management.userexperienceanalytics.user_experience_analytics_metric import (
        UserExperienceAnalyticsMetric,
    )


class UserExperienceAnalyticsCategory(Entity):
    @property
    def insights(self) -> ClientValueCollection[UserExperienceAnalyticsInsight]:
        """Gets the insights property"""
        from office365.intune.devices.management.userexperienceanalytics.user_experience_analytics_insight import (
            UserExperienceAnalyticsInsight,
        )

        return self.properties.get(
            "insights", ClientValueCollection[UserExperienceAnalyticsInsight](UserExperienceAnalyticsInsight)
        )

    @property
    def metric_values(self) -> EntityCollection[UserExperienceAnalyticsMetric]:
        """Gets the metricValues property"""
        from office365.intune.devices.management.userexperienceanalytics.user_experience_analytics_metric import (
            UserExperienceAnalyticsMetric,
        )

        return self.properties.get(
            "metricValues",
            EntityCollection[UserExperienceAnalyticsMetric](
                self.context, UserExperienceAnalyticsMetric, ResourcePath("metricValues", self.resource_path)
            ),
        )

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.UserExperienceAnalyticsCategory"
