from enum import Enum


class ChildSelectability(Enum):
    One = "0"
    Many = "1"
    unknownFutureValue = "2"

    @property
    def entity_type_name(self):
        return "microsoft.graph.security.ChildSelectability"
