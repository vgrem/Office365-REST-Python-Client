from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from office365.entity import Entity
from office365.runtime.paths.resource_path import ResourcePath

if TYPE_CHECKING:
    from office365.intune.devices.management.userexperienceanalytics.user_experience_analytics_category import (
        UserExperienceAnalyticsCategory,
    )


class UserExperienceAnalyticsBaseline(Entity):
    @property
    def created_date_time(self) -> Optional[datetime]:
        """Gets the createdDateTime property"""
        return self.properties.get("createdDateTime", datetime.min)

    @property
    def display_name(self) -> Optional[str]:
        """Gets the displayName property"""
        return self.properties.get("displayName", None)

    @property
    def is_built_in(self) -> Optional[bool]:
        """Gets the isBuiltIn property"""
        return self.properties.get("isBuiltIn", None)

    @property
    def app_health_metrics(self) -> UserExperienceAnalyticsCategory:
        """Gets the appHealthMetrics property"""
        from office365.intune.devices.management.userexperienceanalytics.user_experience_analytics_category import (
            UserExperienceAnalyticsCategory,
        )

        return self.properties.get(
            "appHealthMetrics",
            UserExperienceAnalyticsCategory(self.context, ResourcePath("appHealthMetrics", self.resource_path)),
        )

    @property
    def battery_health_metrics(self) -> UserExperienceAnalyticsCategory:
        """Gets the batteryHealthMetrics property"""
        from office365.intune.devices.management.userexperienceanalytics.user_experience_analytics_category import (
            UserExperienceAnalyticsCategory,
        )

        return self.properties.get(
            "batteryHealthMetrics",
            UserExperienceAnalyticsCategory(self.context, ResourcePath("batteryHealthMetrics", self.resource_path)),
        )

    @property
    def best_practices_metrics(self) -> UserExperienceAnalyticsCategory:
        """Gets the bestPracticesMetrics property"""
        from office365.intune.devices.management.userexperienceanalytics.user_experience_analytics_category import (
            UserExperienceAnalyticsCategory,
        )

        return self.properties.get(
            "bestPracticesMetrics",
            UserExperienceAnalyticsCategory(self.context, ResourcePath("bestPracticesMetrics", self.resource_path)),
        )

    @property
    def device_boot_performance_metrics(self) -> UserExperienceAnalyticsCategory:
        """Gets the deviceBootPerformanceMetrics property"""
        from office365.intune.devices.management.userexperienceanalytics.user_experience_analytics_category import (
            UserExperienceAnalyticsCategory,
        )

        return self.properties.get(
            "deviceBootPerformanceMetrics",
            UserExperienceAnalyticsCategory(
                self.context, ResourcePath("deviceBootPerformanceMetrics", self.resource_path)
            ),
        )

    @property
    def reboot_analytics_metrics(self) -> UserExperienceAnalyticsCategory:
        """Gets the rebootAnalyticsMetrics property"""
        from office365.intune.devices.management.userexperienceanalytics.user_experience_analytics_category import (
            UserExperienceAnalyticsCategory,
        )

        return self.properties.get(
            "rebootAnalyticsMetrics",
            UserExperienceAnalyticsCategory(self.context, ResourcePath("rebootAnalyticsMetrics", self.resource_path)),
        )

    @property
    def resource_performance_metrics(self) -> UserExperienceAnalyticsCategory:
        """Gets the resourcePerformanceMetrics property"""
        from office365.intune.devices.management.userexperienceanalytics.user_experience_analytics_category import (
            UserExperienceAnalyticsCategory,
        )

        return self.properties.get(
            "resourcePerformanceMetrics",
            UserExperienceAnalyticsCategory(
                self.context, ResourcePath("resourcePerformanceMetrics", self.resource_path)
            ),
        )

    @property
    def work_from_anywhere_metrics(self) -> UserExperienceAnalyticsCategory:
        """Gets the workFromAnywhereMetrics property"""
        from office365.intune.devices.management.userexperienceanalytics.user_experience_analytics_category import (
            UserExperienceAnalyticsCategory,
        )

        return self.properties.get(
            "workFromAnywhereMetrics",
            UserExperienceAnalyticsCategory(self.context, ResourcePath("workFromAnywhereMetrics", self.resource_path)),
        )

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.UserExperienceAnalyticsBaseline"
