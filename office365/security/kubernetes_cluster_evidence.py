from __future__ import annotations

from dataclasses import dataclass, field

from office365.runtime.client_value import ClientValue
from office365.security.alerts.evidence import AlertEvidence
from office365.security.alerts.kubernetesplatform import KubernetesPlatform


@dataclass
class KubernetesClusterEvidence(ClientValue):
    cloudResource: AlertEvidence = field(default_factory=AlertEvidence)
    distribution: str | None = None
    name: str | None = None
    platform: KubernetesPlatform = KubernetesPlatform.unknown
    version: str | None = None

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.security.KubernetesClusterEvidence"
