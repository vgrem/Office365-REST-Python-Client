from __future__ import annotations

from dataclasses import dataclass, field

from office365.common.proxied_domain import ProxiedDomain
from office365.runtime.client_value import ClientValue
from office365.runtime.client_value_collection import ClientValueCollection


@dataclass
class WindowsInformationProtectionProxiedDomainCollection(ClientValue):
    displayName: str | None = None
    proxiedDomains: ClientValueCollection[ProxiedDomain] = field(
        default_factory=lambda: ClientValueCollection(ProxiedDomain)
    )

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.WindowsInformationProtectionProxiedDomainCollection"
