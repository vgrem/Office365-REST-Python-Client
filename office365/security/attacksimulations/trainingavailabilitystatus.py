from enum import Enum


class TrainingAvailabilityStatus(Enum):
    unknown = "0"
    notAvailable = "1"
    available = "2"
    archive = "3"
    delete = "4"
    unknownFutureValue = "5"

    @property
    def entity_type_name(self):
        return "microsoft.graph.TrainingAvailabilityStatus"
