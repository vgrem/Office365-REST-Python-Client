from enum import Enum


class AntispamTeamsDirection(Enum):
    unknown = "0"
    inbound = "1"
    outbound = "2"
    intraorg = "3"
    unknownFutureValue = "31"

    @property
    def entity_type_name(self):
        return "microsoft.graph.security.AntispamTeamsDirection"
