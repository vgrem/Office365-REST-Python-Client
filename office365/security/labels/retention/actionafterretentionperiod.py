from enum import Enum


class ActionAfterRetentionPeriod(Enum):
    """ """

    none = "0"
    delete = "1"
    startDispositionReview = "2"
    relabel = "3"
    unknownFutureValue = "4"

    @property
    def entity_type_name(self):
        return "microsoft.graph.security.ActionAfterRetentionPeriod"
