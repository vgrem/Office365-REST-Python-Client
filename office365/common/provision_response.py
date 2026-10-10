from __future__ import annotations

from dataclasses import dataclass

from office365.runtime.client_value import ClientValue


@dataclass
class ProvisionResponse(ClientValue):
    challenge: str | None = None
    deviceId: str | None = None

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.ProvisionResponse"
