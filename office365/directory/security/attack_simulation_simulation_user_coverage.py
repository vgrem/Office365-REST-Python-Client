from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime

from office365.directory.security.attack_simulation_user import AttackSimulationUser
from office365.runtime.client_value import ClientValue


@dataclass
class AttackSimulationSimulationUserCoverage(ClientValue):
    attackSimulationUser: AttackSimulationUser = field(default_factory=AttackSimulationUser)
    clickCount: int | None = None
    compromisedCount: int | None = None
    latestSimulationDateTime: datetime | None = None
    simulationCount: int | None = None

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.AttackSimulationSimulationUserCoverage"
