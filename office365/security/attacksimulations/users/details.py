from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime

from office365.runtime.client_value import ClientValue
from office365.runtime.client_value_collection import ClientValueCollection
from office365.security.attacksimulations.user import AttackSimulationUser
from office365.security.user_simulation_event_info import (
    UserSimulationEventInfo,
)
from office365.security.user_training_event_info import UserTrainingEventInfo


@dataclass
class UserSimulationDetails(ClientValue):
    """Represents a user of a tenant and their online actions in an attack simulation and training campaign.

    Args:
        assignedTrainingsCount (int): Number of trainings assigned to a user in an attack simulation and training
          campaign.
        simulationUser (AttackSimulationUser):
    """

    assignedTrainingsCount: int | None = None
    simulationUser: AttackSimulationUser = field(default_factory=AttackSimulationUser)

    completedTrainingsCount: int | None = None

    compromisedDateTime: datetime | None = None

    inProgressTrainingsCount: int | None = None

    isCompromised: bool | None = None

    reportedPhishDateTime: datetime | None = None

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.UserSimulationDetails"

    trainingEvents: ClientValueCollection[UserTrainingEventInfo] = field(
        default_factory=lambda: ClientValueCollection(UserTrainingEventInfo)
    )

    simulationEvents: ClientValueCollection[UserSimulationEventInfo] = field(
        default_factory=lambda: ClientValueCollection(UserSimulationEventInfo)
    )
