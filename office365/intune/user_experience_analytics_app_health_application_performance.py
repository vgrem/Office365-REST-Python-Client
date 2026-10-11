from __future__ import annotations

from typing import Optional

from office365.entity import Entity


class UserExperienceAnalyticsAppHealthApplicationPerformance(Entity):
    @property
    def active_device_count(self) -> Optional[int]:
        """Gets the activeDeviceCount property"""
        return self.properties.get("activeDeviceCount", None)

    @property
    def app_crash_count(self) -> Optional[int]:
        """Gets the appCrashCount property"""
        return self.properties.get("appCrashCount", None)

    @property
    def app_display_name(self) -> Optional[str]:
        """Gets the appDisplayName property"""
        return self.properties.get("appDisplayName", None)

    @property
    def app_hang_count(self) -> Optional[int]:
        """Gets the appHangCount property"""
        return self.properties.get("appHangCount", None)

    @property
    def app_health_score(self) -> Optional[float]:
        """Gets the appHealthScore property"""
        return self.properties.get("appHealthScore", None)

    @property
    def app_name(self) -> Optional[str]:
        """Gets the appName property"""
        return self.properties.get("appName", None)

    @property
    def app_publisher(self) -> Optional[str]:
        """Gets the appPublisher property"""
        return self.properties.get("appPublisher", None)

    @property
    def app_usage_duration(self) -> Optional[int]:
        """Gets the appUsageDuration property"""
        return self.properties.get("appUsageDuration", None)

    @property
    def mean_time_to_failure_in_minutes(self) -> Optional[int]:
        """Gets the meanTimeToFailureInMinutes property"""
        return self.properties.get("meanTimeToFailureInMinutes", None)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.UserExperienceAnalyticsAppHealthApplicationPerformance"
