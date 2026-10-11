from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from office365.runtime.client_value import ClientValue
from office365.runtime.client_value_collection import ClientValueCollection
from office365.security.dictionary import Dictionary
from office365.security.ip_evidence import IpEvidence
from office365.security.kubernetes_controller_evidence import (
    KubernetesControllerEvidence,
)
from office365.security.kubernetes_namespace_evidence import (
    KubernetesNamespaceEvidence,
)
from office365.security.kubernetes_service_account_evidence import (
    KubernetesServiceAccountEvidence,
)

if TYPE_CHECKING:
    from office365.security.container_evidence import ContainerEvidence


@dataclass
class KubernetesPodEvidence(ClientValue):
    containers: ClientValueCollection[ContainerEvidence] | None = None
    controller: KubernetesControllerEvidence = field(default_factory=KubernetesControllerEvidence)
    ephemeralContainers: ClientValueCollection[ContainerEvidence] | None = None
    initContainers: ClientValueCollection[ContainerEvidence] | None = None
    labels: Dictionary = field(default_factory=Dictionary)
    name: str | None = None
    namespace: KubernetesNamespaceEvidence = field(default_factory=KubernetesNamespaceEvidence)
    podIp: IpEvidence = field(default_factory=IpEvidence)
    serviceAccount: KubernetesServiceAccountEvidence = field(default_factory=KubernetesServiceAccountEvidence)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.security.KubernetesPodEvidence"
