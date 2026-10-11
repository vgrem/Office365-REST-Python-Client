from enum import Enum


class DetectionStatus(Enum):
    detected = "0"
    blocked = "1"
    prevented = "2"
    unknownFutureValue = "31"

    @property
    def entity_type_name(self):
        return "microsoft.graph.security.DetectionStatus"
