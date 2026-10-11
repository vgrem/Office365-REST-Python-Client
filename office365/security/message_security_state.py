from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from office365.runtime.client_value import ClientValue


@dataclass
class MessageSecurityState(ClientValue):
    connectingIP: str | None = None
    deliveryAction: str | None = None
    deliveryLocation: str | None = None
    directionality: str | None = None
    internetMessageId: str | None = None
    messageFingerprint: str | None = None
    messageReceivedDateTime: datetime | None = None
    messageSubject: str | None = None
    networkMessageId: str | None = None

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.MessageSecurityState"
