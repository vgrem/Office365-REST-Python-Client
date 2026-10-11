from enum import Enum


class PayloadDeliveryPlatform(Enum):
    unknown = "0"
    sms = "1"
    email = "2"
    teams = "3"
    unknownFutureValue = "4"

    @property
    def entity_type_name(self):
        return "microsoft.graph.PayloadDeliveryPlatform"
