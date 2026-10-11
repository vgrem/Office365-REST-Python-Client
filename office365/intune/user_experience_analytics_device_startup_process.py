from __future__ import annotations

from typing import Optional

from office365.entity import Entity


class UserExperienceAnalyticsDeviceStartupProcess(Entity):
    @property
    def managed_device_id(self) -> Optional[str]:
        """Gets the managedDeviceId property"""
        return self.properties.get("managedDeviceId", None)

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
    def startup_impact_in_ms(self) -> Optional[int]:
        """Gets the startupImpactInMs property"""
        return self.properties.get("startupImpactInMs", None)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.UserExperienceAnalyticsDeviceStartupProcess"
