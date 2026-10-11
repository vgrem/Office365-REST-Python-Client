from enum import Enum


class TrainingCompletionDuration(Enum):
    week = "7"
    fortnite = "14"
    month = "30"
    unknownFutureValue = "100"

    @property
    def entity_type_name(self):
        return "microsoft.graph.TrainingCompletionDuration"
