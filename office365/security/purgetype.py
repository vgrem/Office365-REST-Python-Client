from enum import Enum


class PurgeType(Enum):
    recoverable = "0"
    unknownFutureValue = "1"
    permanentlyDelete = "2"

    @property
    def entity_type_name(self):
        return "microsoft.graph.security.PurgeType"
