from __future__ import annotations

from dataclasses import dataclass

from office365.runtime.client_value import ClientValue


@dataclass
class AttackSimulationUser(ClientValue):
    displayName: str | None = None
    userId: str | None = None

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.AttackSimulationUser"

    email: str | None = None
