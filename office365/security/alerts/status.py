from enum import Enum


class AlertStatus(Enum):
    """"""

    unknown = "0"
    new = "1"
    inProgress = "2"
    resolved = "3"
    dismissed = "4"
    unknownFutureValue = "127"

    @property
    def entity_type_name(self):
        return "microsoft.graph.AlertStatus"
