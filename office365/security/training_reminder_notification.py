from __future__ import annotations

from dataclasses import dataclass

from office365.runtime.client_value import ClientValue
from office365.security.attacksimulations.notificationdeliveryfrequency import (
    NotificationDeliveryFrequency,
)


@dataclass
class TrainingReminderNotification(ClientValue):
    deliveryFrequency: NotificationDeliveryFrequency = NotificationDeliveryFrequency.unknown

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.TrainingReminderNotification"
