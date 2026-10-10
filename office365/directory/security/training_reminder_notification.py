from __future__ import annotations

from dataclasses import dataclass

from office365.directory.security.attacksimulations.notificationdeliveryfrequency import (
    NotificationDeliveryFrequency,
)
from office365.runtime.client_value import ClientValue


@dataclass
class TrainingReminderNotification(ClientValue):
    deliveryFrequency: NotificationDeliveryFrequency = NotificationDeliveryFrequency.unknown

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.TrainingReminderNotification"
