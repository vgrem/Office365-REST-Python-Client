from enum import Enum


class AlertFeedback(Enum):
    unknown = "0"
    truePositive = "1"
    falsePositive = "2"
    benignPositive = "3"
    unknownFutureValue = "127"

    @property
    def entity_type_name(self):
        return "microsoft.graph.AlertFeedback"
