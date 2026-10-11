from enum import Enum


class SecurityResourceType(Enum):
    unknown = "0"
    attacked = "1"
    related = "2"
    unknownFutureValue = "3"

    @property
    def entity_type_name(self):
        return "microsoft.graph.SecurityResourceType"
