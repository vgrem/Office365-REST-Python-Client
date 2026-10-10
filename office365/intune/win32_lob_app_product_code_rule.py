from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from office365.runtime.client_value import ClientValue

if TYPE_CHECKING:
    from office365.intune.devices.management.mobileapps.win32.ruleoperator import (
        Win32LobAppRuleOperator,
    )


@dataclass
class Win32LobAppProductCodeRule(ClientValue):
    productCode: str | None = None
    productVersion: str | None = None
    productVersionOperator: Win32LobAppRuleOperator = Win32LobAppRuleOperator.notConfigured

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.Win32LobAppProductCodeRule"
