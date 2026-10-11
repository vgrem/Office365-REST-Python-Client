from enum import Enum


class EndUserNotificationPreference(Enum):
    unknown = "0"
    microsoft = "1"
    custom = "2"
    unknownFutureValue = "3"

    @property
    def entity_type_name(self):
        return "microsoft.graph.EndUserNotificationPreference"
