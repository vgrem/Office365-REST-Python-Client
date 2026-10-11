from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from office365.entity import Entity
from office365.entity_collection import EntityCollection
from office365.runtime.paths.resource_path import ResourcePath

if TYPE_CHECKING:
    from office365.intune.devices.configurations.windows.minimum_operating_system import (
        WindowsMinimumOperatingSystem,
    )
    from office365.intune.devices.management.mobileapps.contained_app import (
        MobileContainedApp,
    )
    from office365.intune.devices.management.mobileapps.windows.architecture import (
        WindowsArchitecture,
    )
    from office365.intune.devices.management.mobileapps.windows.devicetype import (
        WindowsDeviceType,
    )


class WindowsUniversalAppX(Entity):
    @property
    def applicable_architectures(self) -> WindowsArchitecture:
        """Gets the applicableArchitectures property"""
        from office365.intune.devices.management.mobileapps.windows.architecture import (
            WindowsArchitecture,
        )

        return self.properties.get("applicableArchitectures", WindowsArchitecture.none)

    @property
    def applicable_device_types(self) -> WindowsDeviceType:
        """Gets the applicableDeviceTypes property"""
        from office365.intune.devices.management.mobileapps.windows.devicetype import (
            WindowsDeviceType,
        )

        return self.properties.get("applicableDeviceTypes", WindowsDeviceType.none)

    @property
    def identity_name(self) -> Optional[str]:
        """Gets the identityName property"""
        return self.properties.get("identityName", None)

    @property
    def identity_publisher_hash(self) -> Optional[str]:
        """Gets the identityPublisherHash property"""
        return self.properties.get("identityPublisherHash", None)

    @property
    def identity_resource_identifier(self) -> Optional[str]:
        """Gets the identityResourceIdentifier property"""
        return self.properties.get("identityResourceIdentifier", None)

    @property
    def identity_version(self) -> Optional[str]:
        """Gets the identityVersion property"""
        return self.properties.get("identityVersion", None)

    @property
    def is_bundle(self) -> Optional[bool]:
        """Gets the isBundle property"""
        return self.properties.get("isBundle", None)

    @property
    def minimum_supported_operating_system(self) -> WindowsMinimumOperatingSystem:
        """Gets the minimumSupportedOperatingSystem property"""
        from office365.intune.devices.configurations.windows.minimum_operating_system import (
            WindowsMinimumOperatingSystem,
        )

        return self.properties.get("minimumSupportedOperatingSystem", WindowsMinimumOperatingSystem())

    @property
    def committed_contained_apps(self) -> EntityCollection[MobileContainedApp]:
        """Gets the committedContainedApps property"""
        from office365.intune.devices.management.mobileapps.contained_app import (
            MobileContainedApp,
        )

        return self.properties.get(
            "committedContainedApps",
            EntityCollection[MobileContainedApp](
                self.context, MobileContainedApp, ResourcePath("committedContainedApps", self.resource_path)
            ),
        )

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.WindowsUniversalAppX"
