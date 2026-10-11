from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from office365.entity import Entity
from office365.entity_collection import EntityCollection
from office365.runtime.paths.resource_path import ResourcePath

if TYPE_CHECKING:
    from office365.intune.devices.compliance.policyplatformtype import (
        PolicyPlatformType,
    )
    from office365.intune.devices.compliance_setting_state import (
        DeviceComplianceSettingState,
    )


class DeviceCompliancePolicySettingStateSummary(Entity):
    @property
    def compliant_device_count(self) -> Optional[int]:
        """Gets the compliantDeviceCount property"""
        return self.properties.get("compliantDeviceCount", None)

    @property
    def conflict_device_count(self) -> Optional[int]:
        """Gets the conflictDeviceCount property"""
        return self.properties.get("conflictDeviceCount", None)

    @property
    def error_device_count(self) -> Optional[int]:
        """Gets the errorDeviceCount property"""
        return self.properties.get("errorDeviceCount", None)

    @property
    def non_compliant_device_count(self) -> Optional[int]:
        """Gets the nonCompliantDeviceCount property"""
        return self.properties.get("nonCompliantDeviceCount", None)

    @property
    def not_applicable_device_count(self) -> Optional[int]:
        """Gets the notApplicableDeviceCount property"""
        return self.properties.get("notApplicableDeviceCount", None)

    @property
    def platform_type(self) -> PolicyPlatformType:
        """Gets the platformType property"""
        from office365.intune.devices.compliance.policyplatformtype import (
            PolicyPlatformType,
        )

        return self.properties.get("platformType", PolicyPlatformType.android)

    @property
    def remediated_device_count(self) -> Optional[int]:
        """Gets the remediatedDeviceCount property"""
        return self.properties.get("remediatedDeviceCount", None)

    @property
    def setting(self) -> Optional[str]:
        """Gets the setting property"""
        return self.properties.get("setting", None)

    @property
    def setting_name(self) -> Optional[str]:
        """Gets the settingName property"""
        return self.properties.get("settingName", None)

    @property
    def unknown_device_count(self) -> Optional[int]:
        """Gets the unknownDeviceCount property"""
        return self.properties.get("unknownDeviceCount", None)

    @property
    def device_compliance_setting_states(self) -> EntityCollection[DeviceComplianceSettingState]:
        """Gets the deviceComplianceSettingStates property"""
        from office365.intune.devices.compliance_setting_state import (
            DeviceComplianceSettingState,
        )

        return self.properties.get(
            "deviceComplianceSettingStates",
            EntityCollection[DeviceComplianceSettingState](
                self.context,
                DeviceComplianceSettingState,
                ResourcePath("deviceComplianceSettingStates", self.resource_path),
            ),
        )

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.DeviceCompliancePolicySettingStateSummary"
