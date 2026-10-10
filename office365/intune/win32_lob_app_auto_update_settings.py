from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from office365.runtime.client_value import ClientValue

if TYPE_CHECKING:
    from office365.intune.devices.management.mobileapps.win32.autoupdatesupersededappsstate import (
        Win32LobAutoUpdateSupersededAppsState,
    )


@dataclass
class Win32LobAppAutoUpdateSettings(ClientValue):
    autoUpdateSupersededAppsState: Win32LobAutoUpdateSupersededAppsState = (
        Win32LobAutoUpdateSupersededAppsState.notConfigured
    )

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.Win32LobAppAutoUpdateSettings"
