from enum import Enum


class DefaultRecordBehavior(Enum):
    """ """

    startLocked = "0"
    startUnlocked = "1"
    unknownFutureValue = "2"

    @property
    def entity_type_name(self):
        return "microsoft.graph.security.DefaultRecordBehavior"
