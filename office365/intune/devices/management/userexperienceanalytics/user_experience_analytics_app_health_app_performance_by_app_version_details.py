from __future__ import annotations

from typing import Optional

from office365.entity import Entity


class UserExperienceAnalyticsAppHealthAppPerformanceByAppVersionDetails(Entity):
    @property
    def app_crash_count(self) -> Optional[int]:
        """Gets the appCrashCount property"""
        return self.properties.get("appCrashCount", None)

    @property
    def app_display_name(self) -> Optional[str]:
        """Gets the appDisplayName property"""
        return self.properties.get("appDisplayName", None)

    @property
    def app_name(self) -> Optional[str]:
        """Gets the appName property"""
        return self.properties.get("appName", None)

    @property
    def app_publisher(self) -> Optional[str]:
        """Gets the appPublisher property"""
        return self.properties.get("appPublisher", None)

    @property
    def app_version(self) -> Optional[str]:
        """Gets the appVersion property"""
        return self.properties.get("appVersion", None)

    @property
    def device_count_with_crashes(self) -> Optional[int]:
        """Gets the deviceCountWithCrashes property"""
        return self.properties.get("deviceCountWithCrashes", None)

    @property
    def is_latest_used_version(self) -> Optional[bool]:
        """Gets the isLatestUsedVersion property"""
        return self.properties.get("isLatestUsedVersion", None)

    @property
    def is_most_used_version(self) -> Optional[bool]:
        """Gets the isMostUsedVersion property"""
        return self.properties.get("isMostUsedVersion", None)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.UserExperienceAnalyticsAppHealthAppPerformanceByAppVersionDetails"
