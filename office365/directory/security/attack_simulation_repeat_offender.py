from __future__ import annotations

from dataclasses import dataclass, field

from office365.directory.security.attack_simulation_user import AttackSimulationUser
from office365.runtime.client_value import ClientValue


@dataclass
class AttackSimulationRepeatOffender(ClientValue):
    attackSimulationUser: AttackSimulationUser = field(default_factory=AttackSimulationUser)
    repeatOffenceCount: int | None = None

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.AttackSimulationRepeatOffender"
