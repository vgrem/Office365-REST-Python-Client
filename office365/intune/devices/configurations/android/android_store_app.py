from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from office365.entity import Entity

if TYPE_CHECKING:
    from office365.intune.devices.configurations.android.minimum_operating_system import (
        AndroidMinimumOperatingSystem,
    )


class AndroidStoreApp(Entity):
    @property
    def app_store_url(self) -> Optional[str]:
        """Gets the appStoreUrl property"""
        return self.properties.get("appStoreUrl", None)

    @property
    def package_id(self) -> Optional[str]:
        """Gets the packageId property"""
        return self.properties.get("packageId", None)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.AndroidStoreApp"

    @property
    def minimum_supported_operating_system(self) -> AndroidMinimumOperatingSystem:
        """Gets the minimumSupportedOperatingSystem property"""
        from office365.intune.devices.configurations.android.minimum_operating_system import (
            AndroidMinimumOperatingSystem,
        )

        return self.properties.get("minimumSupportedOperatingSystem", AndroidMinimumOperatingSystem())
