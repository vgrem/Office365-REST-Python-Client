from __future__ import annotations

from typing import Optional

from office365.entity import Entity


class DeviceConfigurationDeviceStateSummary(Entity):
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
    def remediated_device_count(self) -> Optional[int]:
        """Gets the remediatedDeviceCount property"""
        return self.properties.get("remediatedDeviceCount", None)

    @property
    def unknown_device_count(self) -> Optional[int]:
        """Gets the unknownDeviceCount property"""
        return self.properties.get("unknownDeviceCount", None)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.DeviceConfigurationDeviceStateSummary"
