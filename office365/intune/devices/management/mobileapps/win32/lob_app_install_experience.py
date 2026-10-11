from __future__ import annotations

from dataclasses import dataclass

from office365.intune.devices.management.mobileapps.runasaccounttype import (
    RunAsAccountType,
)
from office365.intune.devices.management.mobileapps.win32.restartbehavior import (
    Win32LobAppRestartBehavior,
)
from office365.runtime.client_value import ClientValue


@dataclass
class Win32LobAppInstallExperience(ClientValue):
    deviceRestartBehavior: Win32LobAppRestartBehavior = Win32LobAppRestartBehavior.basedOnReturnCode
    runAsAccount: RunAsAccountType = RunAsAccountType.system

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.Win32LobAppInstallExperience"
