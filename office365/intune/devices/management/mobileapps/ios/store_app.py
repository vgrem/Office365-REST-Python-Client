from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from office365.entity import Entity

if TYPE_CHECKING:
    from office365.intune.devices.configurations.ios.minimum_operating_system import (
        IosMinimumOperatingSystem,
    )
    from office365.intune.devices.management.mobileapps.ios.ios_device_type import (
        IosDeviceType,
    )


class IosStoreApp(Entity):
    @property
    def applicable_device_type(self) -> IosDeviceType:
        """Gets the applicableDeviceType property"""
        from office365.intune.devices.management.mobileapps.ios.ios_device_type import (
            IosDeviceType,
        )

        return self.properties.get("applicableDeviceType", IosDeviceType())

    @property
    def app_store_url(self) -> Optional[str]:
        """Gets the appStoreUrl property"""
        return self.properties.get("appStoreUrl", None)

    @property
    def bundle_id(self) -> Optional[str]:
        """Gets the bundleId property"""
        return self.properties.get("bundleId", None)

    @property
    def minimum_supported_operating_system(self) -> IosMinimumOperatingSystem:
        """Gets the minimumSupportedOperatingSystem property"""
        from office365.intune.devices.configurations.ios.minimum_operating_system import (
            IosMinimumOperatingSystem,
        )

        return self.properties.get("minimumSupportedOperatingSystem", IosMinimumOperatingSystem())

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.IosStoreApp"
