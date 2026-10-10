from __future__ import annotations

from dataclasses import dataclass

from office365.runtime.client_value import ClientValue


@dataclass
class IPv4Range(ClientValue):
    lowerAddress: str | None = None
    upperAddress: str | None = None

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.IPv4Range"
