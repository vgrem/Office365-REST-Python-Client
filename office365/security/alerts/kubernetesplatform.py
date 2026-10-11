from enum import Enum


class KubernetesPlatform(Enum):
    unknown = "0"
    aks = "1"
    eks = "2"
    gke = "3"
    arc = "4"
    unknownFutureValue = "5"

    @property
    def entity_type_name(self):
        return "microsoft.graph.security.KubernetesPlatform"
