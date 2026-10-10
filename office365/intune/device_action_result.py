from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from office365.intune.devices.management.managed.actionstate import ActionState
from office365.runtime.client_value import ClientValue


@dataclass
class DeviceActionResult(ClientValue):
    actionName: str | None = None
    actionState: ActionState = ActionState.none
    lastUpdatedDateTime: datetime | None = None
    startDateTime: datetime | None = None

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.DeviceActionResult"
