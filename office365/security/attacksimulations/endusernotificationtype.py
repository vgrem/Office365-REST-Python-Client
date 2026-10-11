from enum import Enum


class EndUserNotificationType(Enum):
    unknown = "0"
    positiveReinforcement = "1"
    noTraining = "2"
    trainingAssignment = "3"
    trainingReminder = "4"
    unknownFutureValue = "5"

    @property
    def entity_type_name(self):
        return "microsoft.graph.EndUserNotificationType"
