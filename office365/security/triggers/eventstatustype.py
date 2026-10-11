from enum import Enum


class EventStatusType(Enum):
    pending = "0"
    error = "1"
    success = "2"
    notAvaliable = "3"
    unknownFutureValue = "4"

    @property
    def entity_type_name(self):
        return "microsoft.graph.security.EventStatusType"
