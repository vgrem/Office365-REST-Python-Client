from enum import Enum


class PolicyPivotProperty(Enum):
    none = "0"
    activity = "1"
    location = "2"
    unknownFutureValue = "3"

    @property
    def entity_type_name(self):
        return "microsoft.graph.PolicyPivotProperty"
