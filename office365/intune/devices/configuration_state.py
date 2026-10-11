from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from office365.entity import Entity
from office365.runtime.client_value_collection import ClientValueCollection

if TYPE_CHECKING:
    from office365.intune.devices.compliance.policyplatformtype import (
        PolicyPlatformType,
    )
    from office365.intune.devices.compliance.status import ComplianceStatus
    from office365.intune.devices.management.configuration_setting_state import (
        DeviceConfigurationSettingState,
    )


class DeviceConfigurationState(Entity):
    @property
    def display_name(self) -> Optional[str]:
        """Gets the displayName property"""
        return self.properties.get("displayName", None)

    @property
    def platform_type(self) -> PolicyPlatformType:
        """Gets the platformType property"""
        from office365.intune.devices.compliance.policyplatformtype import (
            PolicyPlatformType,
        )

        return self.properties.get("platformType", PolicyPlatformType.android)

    @property
    def setting_count(self) -> Optional[int]:
        """Gets the settingCount property"""
        return self.properties.get("settingCount", None)

    @property
    def setting_states(self) -> ClientValueCollection[DeviceConfigurationSettingState]:
        """Gets the settingStates property"""
        from office365.intune.devices.management.configuration_setting_state import (
            DeviceConfigurationSettingState,
        )

        return self.properties.get(
            "settingStates", ClientValueCollection[DeviceConfigurationSettingState](DeviceConfigurationSettingState)
        )

    @property
    def state(self) -> ComplianceStatus:
        """Gets the state property"""
        from office365.intune.devices.compliance.status import ComplianceStatus

        return self.properties.get("state", ComplianceStatus.unknown)

    @property
    def version(self) -> Optional[int]:
        """Gets the version property"""
        return self.properties.get("version", None)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.DeviceConfigurationState"
