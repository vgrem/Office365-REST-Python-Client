from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from office365.entity import Entity

if TYPE_CHECKING:
    from office365.intune.devices.management.informationprotection.applicationtype import (
        ApplicationType,
    )


class WindowsInformationProtectionAppLearningSummary(Entity):
    @property
    def application_name(self) -> Optional[str]:
        """Gets the applicationName property"""
        return self.properties.get("applicationName", None)

    @property
    def application_type(self) -> ApplicationType:
        """Gets the applicationType property"""
        from office365.intune.devices.management.informationprotection.applicationtype import (
            ApplicationType,
        )

        return self.properties.get("applicationType", ApplicationType.universal)

    @property
    def device_count(self) -> Optional[int]:
        """Gets the deviceCount property"""
        return self.properties.get("deviceCount", None)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.WindowsInformationProtectionAppLearningSummary"
