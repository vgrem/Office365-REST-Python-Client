from enum import Enum


class EndUserNotificationSettingType(Enum):
    unknown = "0"
    noTraining = "1"
    trainingSelected = "2"
    noNotification = "3"
    unknownFutureValue = "4"

    @property
    def entity_type_name(self):
        return "microsoft.graph.EndUserNotificationSettingType"
