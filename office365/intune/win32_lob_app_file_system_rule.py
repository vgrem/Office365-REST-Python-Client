from __future__ import annotations

from dataclasses import dataclass

from office365.intune.devices.management.mobileapps.win32.filesystemoperationtype import (
    Win32LobAppFileSystemOperationType,
)
from office365.intune.devices.management.mobileapps.win32.ruleoperator import (
    Win32LobAppRuleOperator,
)
from office365.runtime.client_value import ClientValue


@dataclass
class Win32LobAppFileSystemRule(ClientValue):
    check32BitOn64System: bool | None = None
    comparisonValue: str | None = None
    fileOrFolderName: str | None = None
    operationType: Win32LobAppFileSystemOperationType = Win32LobAppFileSystemOperationType.notConfigured
    operator: Win32LobAppRuleOperator = Win32LobAppRuleOperator.notConfigured
    path: str | None = None

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.Win32LobAppFileSystemRule"
