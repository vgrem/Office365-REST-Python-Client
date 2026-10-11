from enum import Enum


class CaseStatus(Enum):
    unknown = "0"
    active = "1"
    pendingDelete = "2"
    closing = "3"
    closed = "4"
    closedWithError = "5"
    unknownFutureValue = "6"

    @property
    def entity_type_name(self):
        return "microsoft.graph.security.CaseStatus"
