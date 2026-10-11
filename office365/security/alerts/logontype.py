from enum import Enum


class LogonType(Enum):
    unknown = "0"
    interactive = "1"
    remoteInteractive = "2"
    network = "3"
    batch = "4"
    service = "5"
    unknownFutureValue = "127"

    @property
    def entity_type_name(self):
        return "microsoft.graph.LogonType"
