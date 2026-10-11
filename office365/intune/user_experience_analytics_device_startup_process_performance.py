from __future__ import annotations

from typing import Optional

from office365.entity import Entity


class UserExperienceAnalyticsDeviceStartupProcessPerformance(Entity):
    @property
    def device_count(self) -> Optional[int]:
        """Gets the deviceCount property"""
        return self.properties.get("deviceCount", None)

    @property
    def median_impact_in_ms(self) -> Optional[int]:
        """Gets the medianImpactInMs property"""
        return self.properties.get("medianImpactInMs", None)

    @property
    def process_name(self) -> Optional[str]:
        """Gets the processName property"""
        return self.properties.get("processName", None)

    @property
    def product_name(self) -> Optional[str]:
        """Gets the productName property"""
        return self.properties.get("productName", None)

    @property
    def publisher(self) -> Optional[str]:
        """Gets the publisher property"""
        return self.properties.get("publisher", None)

    @property
    def total_impact_in_ms(self) -> Optional[int]:
        """Gets the totalImpactInMs property"""
        return self.properties.get("totalImpactInMs", None)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.UserExperienceAnalyticsDeviceStartupProcessPerformance"
