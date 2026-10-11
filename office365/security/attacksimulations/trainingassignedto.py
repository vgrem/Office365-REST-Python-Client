from enum import Enum


class TrainingAssignedTo(Enum):
    none = "0"
    allUsers = "1"
    clickedPayload = "2"
    compromised = "3"
    reportedPhish = "4"
    readButNotClicked = "5"
    didNothing = "6"
    unknownFutureValue = "7"

    @property
    def entity_type_name(self):
        return "microsoft.graph.TrainingAssignedTo"
