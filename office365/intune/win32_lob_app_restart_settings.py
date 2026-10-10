from __future__ import annotations

from dataclasses import dataclass

from office365.runtime.client_value import ClientValue


@dataclass
class Win32LobAppRestartSettings(ClientValue):
    countdownDisplayBeforeRestartInMinutes: int | None = None
    gracePeriodInMinutes: int | None = None
    restartNotificationSnoozeDurationInMinutes: int | None = None

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.Win32LobAppRestartSettings"
