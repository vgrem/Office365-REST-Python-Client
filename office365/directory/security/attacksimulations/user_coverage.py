from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime

from office365.directory.security.attacksimulations.user import AttackSimulationUser
from office365.runtime.client_value import ClientValue


@dataclass
class AttackSimulationSimulationUserCoverage(ClientValue):
    """Represents cumulative simulation data and results for a user in attack simulation and training."""

    attackSimulationUser: AttackSimulationUser = field(default_factory=AttackSimulationUser)

    clickCount: int | None = None

    compromisedCount: int | None = None

    latestSimulationDateTime: datetime | None = None

    simulationCount: int | None = None

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.AttackSimulationSimulationUserCoverage"
