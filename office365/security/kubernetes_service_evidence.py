from __future__ import annotations

from dataclasses import dataclass, field

from office365.runtime.client_value import ClientValue
from office365.runtime.client_value_collection import ClientValueCollection
from office365.security.alerts.kubernetesservicetype import KubernetesServiceType
from office365.security.dictionary import Dictionary
from office365.security.ip_evidence import IpEvidence
from office365.security.kubernetes_namespace_evidence import KubernetesNamespaceEvidence
from office365.security.kubernetes_service_port import KubernetesServicePort


@dataclass
class KubernetesServiceEvidence(ClientValue):
    clusterIP: IpEvidence = field(default_factory=IpEvidence)
    externalIPs: ClientValueCollection[IpEvidence] = field(default_factory=lambda: ClientValueCollection(IpEvidence))
    labels: Dictionary = field(default_factory=Dictionary)
    name: str | None = None
    namespace: KubernetesNamespaceEvidence = field(default_factory=KubernetesNamespaceEvidence)
    selector: Dictionary = field(default_factory=Dictionary)
    servicePorts: ClientValueCollection[KubernetesServicePort] = field(
        default_factory=lambda: ClientValueCollection(KubernetesServicePort)
    )
    serviceType: KubernetesServiceType = KubernetesServiceType.unknown

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.security.KubernetesServiceEvidence"
