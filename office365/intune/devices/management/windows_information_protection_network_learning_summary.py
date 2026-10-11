from __future__ import annotations

from typing import Optional

from office365.entity import Entity


class WindowsInformationProtectionNetworkLearningSummary(Entity):
    @property
    def device_count(self) -> Optional[int]:
        """Gets the deviceCount property"""
        return self.properties.get("deviceCount", None)

    @property
    def url(self) -> Optional[str]:
        """Gets the url property"""
        return self.properties.get("url", None)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.WindowsInformationProtectionNetworkLearningSummary"
