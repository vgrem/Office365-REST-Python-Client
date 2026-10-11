from __future__ import annotations

from dataclasses import dataclass, field

from office365.runtime.client_value import ClientValue
from office365.runtime.types.collections import StringCollection


@dataclass
class MailClusterEvidence(ClientValue):
    clusterBy: str | None = None
    clusterByValue: str | None = None
    emailCount: int | None = None
    networkMessageIds: StringCollection = field(default_factory=StringCollection)
    query: str | None = None
    urn: str | None = None

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.security.MailClusterEvidence"
