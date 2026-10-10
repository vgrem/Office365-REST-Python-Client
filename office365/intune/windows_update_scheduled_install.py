from __future__ import annotations

from dataclasses import dataclass
from datetime import time
from typing import TYPE_CHECKING

from office365.runtime.client_value import ClientValue

if TYPE_CHECKING:
    from office365.intune.devices.configurations.windows.weeklyschedule import (
        WeeklySchedule,
    )


@dataclass
class WindowsUpdateScheduledInstall(ClientValue):
    scheduledInstallDay: WeeklySchedule = WeeklySchedule.userDefined
    scheduledInstallTime: time | None = None

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.WindowsUpdateScheduledInstall"
