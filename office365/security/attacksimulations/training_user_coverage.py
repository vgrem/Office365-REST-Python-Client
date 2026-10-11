from __future__ import annotations

from dataclasses import dataclass, field

from office365.runtime.client_value import ClientValue
from office365.runtime.client_value_collection import ClientValueCollection
from office365.security.attacksimulations.user import AttackSimulationUser
from office365.security.user_training_status_info import (
    UserTrainingStatusInfo,
)


@dataclass
class AttackSimulationTrainingUserCoverage(ClientValue):
    attackSimulationUser: AttackSimulationUser = field(default_factory=AttackSimulationUser)
    userTrainings: ClientValueCollection[UserTrainingStatusInfo] = field(
        default_factory=lambda: ClientValueCollection(UserTrainingStatusInfo)
    )

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.AttackSimulationTrainingUserCoverage"
