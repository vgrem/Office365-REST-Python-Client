from __future__ import annotations

from dataclasses import dataclass

from office365.runtime.client_value import ClientValue


@dataclass
class AzureResourceEvidence(ClientValue):
    resourceId: str | None = None
    resourceName: str | None = None
    resourceType: str | None = None

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.security.AzureResourceEvidence"
