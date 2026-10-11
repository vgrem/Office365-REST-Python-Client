from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from office365.entity import Entity
from office365.runtime.client_value_collection import ClientValueCollection
from office365.runtime.types.collections import StringCollection

if TYPE_CHECKING:
    from office365.intune.devices.configurations.macos.mac_os_minimum_operating_system import (
        MacOSMinimumOperatingSystem,
    )
    from office365.intune.devices.management.mobileapps.macos.mac_os_lob_child_app import (
        MacOSLobChildApp,
    )


class MacOSLobApp(Entity):
    @property
    def build_number(self) -> Optional[str]:
        """Gets the buildNumber property"""
        return self.properties.get("buildNumber", None)

    @property
    def bundle_id(self) -> Optional[str]:
        """Gets the bundleId property"""
        return self.properties.get("bundleId", None)

    @property
    def child_apps(self) -> ClientValueCollection[MacOSLobChildApp]:
        """Gets the childApps property"""
        from office365.intune.devices.management.mobileapps.macos.mac_os_lob_child_app import (
            MacOSLobChildApp,
        )

        return self.properties.get("childApps", ClientValueCollection[MacOSLobChildApp](MacOSLobChildApp))

    @property
    def ignore_version_detection(self) -> Optional[bool]:
        """Gets the ignoreVersionDetection property"""
        return self.properties.get("ignoreVersionDetection", None)

    @property
    def install_as_managed(self) -> Optional[bool]:
        """Gets the installAsManaged property"""
        return self.properties.get("installAsManaged", None)

    @property
    def md5_hash(self) -> StringCollection:
        """Gets the md5Hash property"""
        return self.properties.get("md5Hash", StringCollection())

    @property
    def md5_hash_chunk_size(self) -> Optional[int]:
        """Gets the md5HashChunkSize property"""
        return self.properties.get("md5HashChunkSize", None)

    @property
    def minimum_supported_operating_system(self) -> Optional[MacOSMinimumOperatingSystem]:
        """Gets the minimumSupportedOperatingSystem property"""
        return self.properties.get("minimumSupportedOperatingSystem", None)

    @property
    def version_number(self) -> Optional[str]:
        """Gets the versionNumber property"""
        return self.properties.get("versionNumber", None)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.MacOSLobApp"
