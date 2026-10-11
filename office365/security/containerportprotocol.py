from enum import Enum


class ContainerPortProtocol(Enum):
    udp = "0"
    tcp = "1"
    sctp = "2"
    unknownFutureValue = "3"

    @property
    def entity_type_name(self):
        return "microsoft.graph.security.ContainerPortProtocol"
