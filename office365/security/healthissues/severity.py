from enum import Enum


class HealthIssueSeverity(Enum):
    low = "1"
    medium = "2"
    high = "3"
    unknownFutureValue = "4"

    @property
    def entity_type_name(self):
        return "microsoft.graph.security.HealthIssueSeverity"
