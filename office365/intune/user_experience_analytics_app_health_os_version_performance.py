from __future__ import annotations

from typing import Optional

from office365.entity import Entity


class UserExperienceAnalyticsAppHealthOSVersionPerformance(Entity):
    @property
    def active_device_count(self) -> Optional[int]:
        """Gets the activeDeviceCount property"""
        return self.properties.get("activeDeviceCount", None)

    @property
    def mean_time_to_failure_in_minutes(self) -> Optional[int]:
        """Gets the meanTimeToFailureInMinutes property"""
        return self.properties.get("meanTimeToFailureInMinutes", None)

    @property
    def os_build_number(self) -> Optional[str]:
        """Gets the osBuildNumber property"""
        return self.properties.get("osBuildNumber", None)

    @property
    def os_version(self) -> Optional[str]:
        """Gets the osVersion property"""
        return self.properties.get("osVersion", None)

    @property
    def os_version_app_health_score(self) -> Optional[float]:
        """Gets the osVersionAppHealthScore property"""
        return self.properties.get("osVersionAppHealthScore", None)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.UserExperienceAnalyticsAppHealthOSVersionPerformance"
