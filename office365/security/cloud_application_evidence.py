from __future__ import annotations

from dataclasses import dataclass, field

from office365.runtime.client_value import ClientValue
from office365.security.stream import Stream


@dataclass
class CloudApplicationEvidence(ClientValue):
    appId: int | None = None
    displayName: str | None = None
    instanceId: int | None = None
    instanceName: str | None = None
    saasAppId: int | None = None
    stream: Stream = field(default_factory=Stream)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.security.CloudApplicationEvidence"
