from __future__ import annotations

from dataclasses import dataclass

from office365.runtime.client_value import ClientValue


@dataclass
class ServicePrincipalEvidence(ClientValue):
    appId: str | None = None
    appOwnerTenantId: str | None = None
    servicePrincipalName: str | None = None
    servicePrincipalObjectId: str | None = None
    tenantId: str | None = None

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.security.ServicePrincipalEvidence"
