from enum import Enum


class AlertSeverity(Enum):
    unknown = "0"
    informational = "1"
    low = "2"
    medium = "3"
    high = "4"
    unknownFutureValue = "127"

    @property
    def entity_type_name(self):
        return "microsoft.graph.AlertSeverity"
