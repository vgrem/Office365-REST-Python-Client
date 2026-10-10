from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from office365.directory.security.container_image_evidence import ContainerImageEvidence
from office365.runtime.client_value import ClientValue
from office365.runtime.types.collections import StringCollection

if TYPE_CHECKING:
    from office365.directory.security.kubernetes_pod_evidence import (
        KubernetesPodEvidence,
    )


@dataclass
class ContainerEvidence(ClientValue):
    args: StringCollection = field(default_factory=StringCollection)
    command: StringCollection = field(default_factory=StringCollection)
    containerId: str | None = None
    image: ContainerImageEvidence = field(default_factory=ContainerImageEvidence)
    isPrivileged: bool | None = None
    name: str | None = None
    pod: KubernetesPodEvidence | None = None

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.security.ContainerEvidence"
