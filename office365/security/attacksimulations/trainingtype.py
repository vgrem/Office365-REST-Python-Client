from enum import Enum


class TrainingType(Enum):
    unknown = "0"
    phishing = "1"
    unknownFutureValue = "2"

    @property
    def entity_type_name(self):
        return "microsoft.graph.TrainingType"
