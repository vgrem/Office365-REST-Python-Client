from __future__ import annotations

from dataclasses import dataclass

from office365.runtime.client_value import ClientValue


@dataclass
class Principal(ClientValue):
    email: str | None = None
    entraDisplayName: str | None = None
    entraId: str | None = None
    externalId: str | None = None
    externalName: str | None = None
    tenantId: str | None = None
    upn: str | None = None

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.externalConnectors.Principal"
