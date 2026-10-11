from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from office365.entity import Entity

if TYPE_CHECKING:
    from office365.intune.devices.configurations.android.minimum_operating_system import (
        AndroidMinimumOperatingSystem,
    )


class ManagedAndroidLobApp(Entity):
    @property
    def minimum_supported_operating_system(self) -> AndroidMinimumOperatingSystem:
        """Gets the minimumSupportedOperatingSystem property"""
        from office365.intune.devices.configurations.android.minimum_operating_system import (
            AndroidMinimumOperatingSystem,
        )

        return self.properties.get("minimumSupportedOperatingSystem", AndroidMinimumOperatingSystem())

    @property
    def package_id(self) -> Optional[str]:
        """Gets the packageId property"""
        return self.properties.get("packageId", None)

    @property
    def version_code(self) -> Optional[str]:
        """Gets the versionCode property"""
        return self.properties.get("versionCode", None)

    @property
    def version_name(self) -> Optional[str]:
        """Gets the versionName property"""
        return self.properties.get("versionName", None)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.ManagedAndroidLobApp"
