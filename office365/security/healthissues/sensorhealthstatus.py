from enum import Enum


class SensorHealthStatus(Enum):
    healthy = "1"
    notHealthyLow = "2"
    notHealthyMedium = "3"
    notHealthyHigh = "4"
    unknownFutureValue = "5"

    @property
    def entity_type_name(self):
        return "microsoft.graph.security.SensorHealthStatus"
