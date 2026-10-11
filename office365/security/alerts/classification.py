from enum import Enum


class AlertClassification(Enum):
    unknown = "0"
    falsePositive = "10"
    truePositive = "20"
    informationalExpectedActivity = "30"
    unknownFutureValue = "39"

    @property
    def entity_type_name(self):
        return "microsoft.graph.security.AlertClassification"
