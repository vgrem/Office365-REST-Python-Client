from __future__ import annotations

from dataclasses import dataclass

from office365.runtime.client_value import ClientValue


@dataclass
class HostReputationRule(ClientValue):
    description: str | None = None
    name: str | None = None
    relatedDetailsUrl: str | None = None

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.security.HostReputationRule"
