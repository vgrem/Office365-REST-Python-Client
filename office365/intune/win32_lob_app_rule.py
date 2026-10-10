from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from office365.runtime.client_value import ClientValue

if TYPE_CHECKING:
    from office365.intune.devices.management.mobileapps.win32.ruletype import (
        Win32LobAppRuleType,
    )


@dataclass
class Win32LobAppRule(ClientValue):
    ruleType: Win32LobAppRuleType = Win32LobAppRuleType.detection

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.Win32LobAppRule"
