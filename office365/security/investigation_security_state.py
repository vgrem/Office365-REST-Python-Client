from __future__ import annotations

from dataclasses import dataclass

from office365.runtime.client_value import ClientValue


@dataclass
class InvestigationSecurityState(ClientValue):
    name: str | None = None
    status: str | None = None

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.InvestigationSecurityState"
