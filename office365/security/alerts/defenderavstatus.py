from enum import Enum


class DefenderAvStatus(Enum):
    notReporting = "0"
    disabled = "1"
    notUpdated = "2"
    updated = "3"
    unknown = "4"
    notSupported = "1000"
    unknownFutureValue = "1023"

    @property
    def entity_type_name(self):
        return "microsoft.graph.security.DefenderAvStatus"
