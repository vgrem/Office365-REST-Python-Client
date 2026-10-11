from enum import Enum


class TrainingStatus(Enum):
    unknown = "0"
    assigned = "1"
    inProgress = "2"
    completed = "3"
    overdue = "4"
    unknownFutureValue = "5"

    @property
    def entity_type_name(self):
        return "microsoft.graph.TrainingStatus"
