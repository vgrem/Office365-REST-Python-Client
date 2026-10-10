from __future__ import annotations

from dataclasses import dataclass

from office365.intune.devices.management.mobileapps.win32.registryruleoperationtype import (
    Win32LobAppRegistryRuleOperationType,
)
from office365.intune.devices.management.mobileapps.win32.ruleoperator import (
    Win32LobAppRuleOperator,
)
from office365.runtime.client_value import ClientValue


@dataclass
class Win32LobAppRegistryRule(ClientValue):
    check32BitOn64System: bool | None = None
    comparisonValue: str | None = None
    keyPath: str | None = None
    operationType: Win32LobAppRegistryRuleOperationType = Win32LobAppRegistryRuleOperationType.notConfigured
    operator: Win32LobAppRuleOperator = Win32LobAppRuleOperator.notConfigured
    valueName: str | None = None

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.Win32LobAppRegistryRule"
