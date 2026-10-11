from enum import Enum


class BehaviorDuringRetentionPeriod(Enum):
    """ """

    none = "-1"
    doNotRetain = "0"
    retainAsRecord = "2"
    unknownFutureValue = "4"
    retain = "1"
    retainAsRegulatoryRecord = "3"

    @property
    def entity_type_name(self):
        return "microsoft.graph.security.BehaviorDuringRetentionPeriod"
