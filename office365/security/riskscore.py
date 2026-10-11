from enum import Enum


class DeviceRiskScore(Enum):
    none = "0"
    informational = "5"
    low = "10"
    medium = "20"
    high = "30"
    unknownFutureValue = "31"

    @property
    def entity_type_name(self):
        return "microsoft.graph.security.DeviceRiskScore"
