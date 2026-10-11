from enum import Enum


class ProtectionScopeState(Enum):
    notModified = "0"
    modified = "1"
    unknownFutureValue = "2"

    @property
    def entity_type_name(self):
        return "microsoft.graph.ProtectionScopeState"
