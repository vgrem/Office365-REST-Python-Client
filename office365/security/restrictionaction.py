from enum import Enum


class RestrictionAction(Enum):
    warn = "0"
    audit = "1"
    block = "2"

    @property
    def entity_type_name(self):
        return "microsoft.graph.RestrictionAction"
