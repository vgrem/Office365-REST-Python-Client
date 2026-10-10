from __future__ import annotations

from dataclasses import dataclass

from office365.runtime.client_value import ClientValue


@dataclass
class ExternalDomainFederation(ClientValue):
    displayName: str | None = None
    domainName: str | None = None
    issuerUri: str | None = None

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.ExternalDomainFederation"
