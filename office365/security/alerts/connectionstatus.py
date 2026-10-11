from enum import Enum


class ConnectionStatus(Enum):
    unknown = "0"
    attempted = "1"
    succeeded = "2"
    blocked = "3"
    failed = "4"
    unknownFutureValue = "127"

    @property
    def entity_type_name(self):
        return "microsoft.graph.ConnectionStatus"
