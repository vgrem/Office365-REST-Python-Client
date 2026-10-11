from __future__ import annotations

from dataclasses import dataclass, field

from office365.runtime.client_value import ClientValue
from office365.runtime.client_value_collection import ClientValueCollection


@dataclass
class ActiveDirectoryDomainEvidence(ClientValue):
    activeDirectoryDomainName: str | None = None
    trustedDomains: ClientValueCollection[ActiveDirectoryDomainEvidence] = field(
        default_factory=lambda: ClientValueCollection(ActiveDirectoryDomainEvidence)
    )

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.security.ActiveDirectoryDomainEvidence"
