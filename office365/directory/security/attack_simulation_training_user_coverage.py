from __future__ import annotations

from dataclasses import dataclass, field

from office365.directory.security.attacksimulations.user import AttackSimulationUser
from office365.runtime.client_value import ClientValue


@dataclass
class AttackSimulationTrainingUserCoverage(ClientValue):
    attackSimulationUser: AttackSimulationUser = field(default_factory=AttackSimulationUser)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.AttackSimulationTrainingUserCoverage"
