from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from office365.entity import Entity

if TYPE_CHECKING:
    from office365.intune.devices.management.userexperienceanalytics.healthstate import (
        UserExperienceAnalyticsHealthState,
    )


class UserExperienceAnalyticsModelScores(Entity):
    @property
    def app_reliability_score(self) -> Optional[float]:
        """Gets the appReliabilityScore property"""
        return self.properties.get("appReliabilityScore", None)

    @property
    def battery_health_score(self) -> Optional[float]:
        """Gets the batteryHealthScore property"""
        return self.properties.get("batteryHealthScore", None)

    @property
    def endpoint_analytics_score(self) -> Optional[float]:
        """Gets the endpointAnalyticsScore property"""
        return self.properties.get("endpointAnalyticsScore", None)

    @property
    def health_status(self) -> UserExperienceAnalyticsHealthState:
        """Gets the healthStatus property"""
        from office365.intune.devices.management.userexperienceanalytics.healthstate import (
            UserExperienceAnalyticsHealthState,
        )

        return self.properties.get("healthStatus", UserExperienceAnalyticsHealthState.unknown)

    @property
    def manufacturer(self) -> Optional[str]:
        """Gets the manufacturer property"""
        return self.properties.get("manufacturer", None)

    @property
    def model(self) -> Optional[str]:
        """Gets the model property"""
        return self.properties.get("model", None)

    @property
    def model_device_count(self) -> Optional[int]:
        """Gets the modelDeviceCount property"""
        return self.properties.get("modelDeviceCount", None)

    @property
    def startup_performance_score(self) -> Optional[float]:
        """Gets the startupPerformanceScore property"""
        return self.properties.get("startupPerformanceScore", None)

    @property
    def work_from_anywhere_score(self) -> Optional[float]:
        """Gets the workFromAnywhereScore property"""
        return self.properties.get("workFromAnywhereScore", None)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.UserExperienceAnalyticsModelScores"
