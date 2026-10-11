from enum import Enum


class NotificationDeliveryFrequency(Enum):
    unknown = "0"
    weekly = "1"
    biWeekly = "2"
    unknownFutureValue = "3"

    @property
    def entity_type_name(self):
        return "microsoft.graph.NotificationDeliveryFrequency"
