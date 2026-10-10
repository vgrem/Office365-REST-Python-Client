from __future__ import annotations

from dataclasses import dataclass

from office365.runtime.client_value import ClientValue


@dataclass
class AttackSimulationUser(ClientValue):
    """
    Represents a user in an attack simulation and training campaign.
    """

    displayName: str | None = None
    email: str | None = None
    userId: str | None = None

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.AttackSimulationUser"
