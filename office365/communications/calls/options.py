from __future__ import annotations

from dataclasses import dataclass

from office365.runtime.client_value import ClientValue


@dataclass
class CallOptions(ClientValue):
    """Represents an abstract base class that contains the optional features for a call.

    Fields:
        hideBotAfterEscalation: Indicates whether to hide the app after the call is escalated.
        isContentSharingNotificationEnabled: Indicates whether content sharing notifications should be
            enabled for the call.
    """

    hideBotAfterEscalation: bool | None = None
    isContentSharingNotificationEnabled: bool | None = None

    isDeltaRosterEnabled: bool | None = None

    isInteractiveRosterEnabled: bool | None = None

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.CallOptions"
