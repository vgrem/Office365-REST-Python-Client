from enum import Enum


class KubernetesServiceType(Enum):
    unknown = "0"
    clusterIP = "1"
    externalName = "2"
    nodePort = "3"
    loadBalancer = "4"
    unknownFutureValue = "31"

    @property
    def entity_type_name(self):
        return "microsoft.graph.security.KubernetesServiceType"
