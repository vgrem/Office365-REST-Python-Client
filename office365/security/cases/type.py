from enum import Enum


class CaseType(Enum):
    standard = "1"
    premium = "2"
    unknownFutureValue = "3"

    @property
    def entity_type_name(self):
        return "microsoft.graph.security.CaseType"
