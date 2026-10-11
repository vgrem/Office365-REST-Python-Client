from enum import Enum


class EmailRole(Enum):
    unknown = "0"
    sender = "1"
    recipient = "2"
    unknownFutureValue = "127"

    @property
    def entity_type_name(self):
        return "microsoft.graph.EmailRole"
