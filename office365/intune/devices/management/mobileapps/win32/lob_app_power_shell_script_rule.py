from __future__ import annotations

from dataclasses import dataclass

from office365.intune.devices.management.mobileapps.runasaccounttype import (
    RunAsAccountType,
)
from office365.intune.devices.management.mobileapps.win32.powershellscriptruleoperationtype import (
    Win32LobAppPowerShellScriptRuleOperationType,
)
from office365.intune.devices.management.mobileapps.win32.ruleoperator import (
    Win32LobAppRuleOperator,
)
from office365.runtime.client_value import ClientValue


@dataclass
class Win32LobAppPowerShellScriptRule(ClientValue):
    comparisonValue: str | None = None
    displayName: str | None = None
    enforceSignatureCheck: bool | None = None
    operationType: Win32LobAppPowerShellScriptRuleOperationType = (
        Win32LobAppPowerShellScriptRuleOperationType.notConfigured
    )
    operator: Win32LobAppRuleOperator = Win32LobAppRuleOperator.notConfigured
    runAs32Bit: bool | None = None
    runAsAccount: RunAsAccountType = RunAsAccountType.system
    scriptContent: str | None = None

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.Win32LobAppPowerShellScriptRule"
