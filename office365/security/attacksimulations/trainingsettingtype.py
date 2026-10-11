from enum import Enum


class TrainingSettingType(Enum):
    microsoftCustom = "0"
    microsoftManaged = "1"
    noTraining = "2"
    custom = "3"
    unknownFutureValue = "4"

    @property
    def entity_type_name(self):
        return "microsoft.graph.TrainingSettingType"
