from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from office365.runtime.client_value import ClientValue

if TYPE_CHECKING:
    from office365.directory.security.delivery_action import DeliveryAction
    from office365.directory.security.delivery_location import DeliveryLocation


@dataclass
class AnalyzedEmailDeliveryDetail(ClientValue):
    latestThreats: str | None = None
    originalThreats: str | None = None

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.security.AnalyzedEmailDeliveryDetail"

    action: DeliveryAction = DeliveryAction.unknown

    location: DeliveryLocation = DeliveryLocation.unknown
