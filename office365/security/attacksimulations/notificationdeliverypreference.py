from enum import Enum


class NotificationDeliveryPreference(Enum):
    unknown = "0"
    deliverImmedietly = "1"
    deliverAfterCampaignEnd = "2"
    unknownFutureValue = "3"

    @property
    def entity_type_name(self):
        return "microsoft.graph.NotificationDeliveryPreference"
