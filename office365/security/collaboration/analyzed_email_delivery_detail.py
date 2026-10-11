from __future__ import annotations

from dataclasses import dataclass

from office365.runtime.client_value import ClientValue
from office365.security.delivery_action import DeliveryAction
from office365.security.delivery_location import DeliveryLocation


@dataclass
class AnalyzedEmailDeliveryDetail(ClientValue):
    latestThreats: str | None = None
    originalThreats: str | None = None

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.security.AnalyzedEmailDeliveryDetail"

    action: DeliveryAction = DeliveryAction.unknown

    location: DeliveryLocation = DeliveryLocation.unknown
