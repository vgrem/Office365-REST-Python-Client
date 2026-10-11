from __future__ import annotations

from dataclasses import dataclass

from office365.runtime.client_value import ClientValue
from office365.security.attacksimulations.notificationdeliverypreference import (
    NotificationDeliveryPreference,
)


@dataclass
class PositiveReinforcementNotification(ClientValue):
    deliveryPreference: NotificationDeliveryPreference = NotificationDeliveryPreference.unknown

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.PositiveReinforcementNotification"
