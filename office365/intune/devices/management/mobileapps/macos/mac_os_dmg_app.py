from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from office365.entity import Entity
from office365.runtime.client_value_collection import ClientValueCollection

if TYPE_CHECKING:
    from office365.intune.devices.configurations.macos.mac_os_minimum_operating_system import (
        MacOSMinimumOperatingSystem,
    )
    from office365.intune.devices.management.mobileapps.macos.mac_os_included_app import (
        MacOSIncludedApp,
    )


class MacOSDmgApp(Entity):
    @property
    def ignore_version_detection(self) -> Optional[bool]:
        """Gets the ignoreVersionDetection property"""
        return self.properties.get("ignoreVersionDetection", None)

    @property
    def included_apps(self) -> ClientValueCollection[MacOSIncludedApp]:
        """Gets the includedApps property"""
        from office365.intune.devices.management.mobileapps.macos.mac_os_included_app import (
            MacOSIncludedApp,
        )

        return self.properties.get("includedApps", ClientValueCollection[MacOSIncludedApp](MacOSIncludedApp))

    @property
    def minimum_supported_operating_system(self) -> Optional[MacOSMinimumOperatingSystem]:
        """Gets the minimumSupportedOperatingSystem property"""
        return self.properties.get("minimumSupportedOperatingSystem", None)

    @property
    def primary_bundle_id(self) -> Optional[str]:
        """Gets the primaryBundleId property"""
        return self.properties.get("primaryBundleId", None)

    @property
    def primary_bundle_version(self) -> Optional[str]:
        """Gets the primaryBundleVersion property"""
        return self.properties.get("primaryBundleVersion", None)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.MacOSDmgApp"
