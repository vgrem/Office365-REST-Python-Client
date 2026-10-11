from __future__ import annotations

from typing import TYPE_CHECKING

from office365.entity import Entity

if TYPE_CHECKING:
    from office365.admin.microsoft365.appsupdatechanneltype import AppsUpdateChannelType
    from office365.intune.devices.management.mobileapps.apps_installation_options_for_mac import (
        AppsInstallationOptionsForMac,
    )
    from office365.intune.devices.management.mobileapps.apps_installation_options_for_windows import (
        AppsInstallationOptionsForWindows,
    )


class M365AppsInstallationOptions(Entity):
    @property
    def apps_for_mac(self) -> AppsInstallationOptionsForMac:
        """Gets the appsForMac property"""
        from office365.intune.devices.management.mobileapps.apps_installation_options_for_mac import (
            AppsInstallationOptionsForMac,
        )

        return self.properties.get("appsForMac", AppsInstallationOptionsForMac())

    @property
    def apps_for_windows(self) -> AppsInstallationOptionsForWindows:
        """Gets the appsForWindows property"""
        from office365.intune.devices.management.mobileapps.apps_installation_options_for_windows import (
            AppsInstallationOptionsForWindows,
        )

        return self.properties.get("appsForWindows", AppsInstallationOptionsForWindows())

    @property
    def update_channel(self) -> AppsUpdateChannelType:
        """Gets the updateChannel property"""
        from office365.admin.microsoft365.appsupdatechanneltype import (
            AppsUpdateChannelType,
        )

        return self.properties.get("updateChannel", AppsUpdateChannelType.current)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.M365AppsInstallationOptions"
