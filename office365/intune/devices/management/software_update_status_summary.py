from __future__ import annotations

from typing import Optional

from office365.entity import Entity


class SoftwareUpdateStatusSummary(Entity):
    @property
    def compliant_device_count(self) -> Optional[int]:
        """Gets the compliantDeviceCount property"""
        return self.properties.get("compliantDeviceCount", None)

    @property
    def compliant_user_count(self) -> Optional[int]:
        """Gets the compliantUserCount property"""
        return self.properties.get("compliantUserCount", None)

    @property
    def conflict_device_count(self) -> Optional[int]:
        """Gets the conflictDeviceCount property"""
        return self.properties.get("conflictDeviceCount", None)

    @property
    def conflict_user_count(self) -> Optional[int]:
        """Gets the conflictUserCount property"""
        return self.properties.get("conflictUserCount", None)

    @property
    def display_name(self) -> Optional[str]:
        """Gets the displayName property"""
        return self.properties.get("displayName", None)

    @property
    def error_device_count(self) -> Optional[int]:
        """Gets the errorDeviceCount property"""
        return self.properties.get("errorDeviceCount", None)

    @property
    def error_user_count(self) -> Optional[int]:
        """Gets the errorUserCount property"""
        return self.properties.get("errorUserCount", None)

    @property
    def non_compliant_device_count(self) -> Optional[int]:
        """Gets the nonCompliantDeviceCount property"""
        return self.properties.get("nonCompliantDeviceCount", None)

    @property
    def non_compliant_user_count(self) -> Optional[int]:
        """Gets the nonCompliantUserCount property"""
        return self.properties.get("nonCompliantUserCount", None)

    @property
    def not_applicable_device_count(self) -> Optional[int]:
        """Gets the notApplicableDeviceCount property"""
        return self.properties.get("notApplicableDeviceCount", None)

    @property
    def not_applicable_user_count(self) -> Optional[int]:
        """Gets the notApplicableUserCount property"""
        return self.properties.get("notApplicableUserCount", None)

    @property
    def remediated_device_count(self) -> Optional[int]:
        """Gets the remediatedDeviceCount property"""
        return self.properties.get("remediatedDeviceCount", None)

    @property
    def remediated_user_count(self) -> Optional[int]:
        """Gets the remediatedUserCount property"""
        return self.properties.get("remediatedUserCount", None)

    @property
    def unknown_device_count(self) -> Optional[int]:
        """Gets the unknownDeviceCount property"""
        return self.properties.get("unknownDeviceCount", None)

    @property
    def unknown_user_count(self) -> Optional[int]:
        """Gets the unknownUserCount property"""
        return self.properties.get("unknownUserCount", None)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.SoftwareUpdateStatusSummary"
