from __future__ import annotations

from typing import Optional

from office365.entity import Entity


class EBookInstallSummary(Entity):
    @property
    def failed_device_count(self) -> Optional[int]:
        """Gets the failedDeviceCount property"""
        return self.properties.get("failedDeviceCount", None)

    @property
    def failed_user_count(self) -> Optional[int]:
        """Gets the failedUserCount property"""
        return self.properties.get("failedUserCount", None)

    @property
    def installed_device_count(self) -> Optional[int]:
        """Gets the installedDeviceCount property"""
        return self.properties.get("installedDeviceCount", None)

    @property
    def installed_user_count(self) -> Optional[int]:
        """Gets the installedUserCount property"""
        return self.properties.get("installedUserCount", None)

    @property
    def not_installed_device_count(self) -> Optional[int]:
        """Gets the notInstalledDeviceCount property"""
        return self.properties.get("notInstalledDeviceCount", None)

    @property
    def not_installed_user_count(self) -> Optional[int]:
        """Gets the notInstalledUserCount property"""
        return self.properties.get("notInstalledUserCount", None)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.EBookInstallSummary"
