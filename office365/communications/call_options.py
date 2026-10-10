from __future__ import annotations

from dataclasses import dataclass

from office365.runtime.client_value import ClientValue


@dataclass
class CallOptions(ClientValue):
    hideBotAfterEscalation: bool | None = None
    isContentSharingNotificationEnabled: bool | None = None
    isDeltaRosterEnabled: bool | None = None
    isInteractiveRosterEnabled: bool | None = None

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.CallOptions"
